import json_repair
import json
import re
import io
import base64
import requests
import cudf
import pandas as pd
from .constants import BASE_URL, DATETIME_FORMATS
import asyncio
from .formatting_utilities import parse_markdown_table
from .cache_config import cache
from fastapi import HTTPException
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor



def get_data_from_api(endpoint):
    response = requests.get(f"{BASE_URL}/{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from {endpoint}: {response.text}")
    
def get_dataframe() -> cudf.DataFrame:
    df = cache.get('current_df')
    if df is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    return df

def extract_table_from_content(content):
    table_data = None
    elements = extract_content(content)
    for element_type, element in elements:
        if element_type == 'table':
            table_data = parse_markdown_table(element)
            break
    return table_data

def is_timeseries(df: cudf.DataFrame) -> bool:
    try:
        datetime_cols = df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns
        if not datetime_cols.empty:
            return True
    except Exception as e:
        return(f"Error checking DataFrame columns: {str(e)}")
    return False

def run_async_in_sync(coroutine):
    def run_in_new_loop(coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_in_new_loop, coroutine)
        return future.result()
    
def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()
        
def resample_df(df):
    datetime_cols = df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns.tolist()
    
    if not datetime_cols:
        raise ValueError("No datetime columns found in the DataFrame")

    resampled_dfs = []

    for col in datetime_cols:
        freq = df[col].diff().dt.seconds.mode().values[0] / 60
                      
        if freq < 1440:
            numeric_cols = df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns.tolist()
            agg_dict = {colu: 'mean' for colu in numeric_cols if colu != col}
            
            for colu in agg_dict.keys():
                if colu not in df.columns:
                    raise ValueError(f"Column '{colu}' specified in aggregation dictionary not found in the DataFrame")

            categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
            df_pandas = df.to_pandas() 
            for cat_col in categorical_cols:
                df_pandas[cat_col] = df_pandas[cat_col].ffill()

      
            df = cudf.DataFrame.from_pandas(df_pandas)  
            df = df.set_index(col)
            
            resampled = df.resample('D').agg(agg_dict).reset_index()

            for colu in resampled.columns:
                if resampled[colu].dtype in ['float64', 'float32']:
                    resampled[colu] = resampled[colu].round(2)

            resampled_pandas = resampled.to_pandas()
            for cat_col in categorical_cols:
                resampled_pandas[cat_col] = df_pandas[cat_col].reindex(resampled_pandas.index, method='ffill')
            
            resampled_dfs.append(resampled_pandas)

    if not resampled_dfs:
        raise ValueError("No columns met the frequency condition for resampling")
    
    final_resampled_df = pd.concat(resampled_dfs, axis=1)
    
    final_resampled_df = cudf.DataFrame.from_pandas(final_resampled_df)
    return final_resampled_df

def sample_data(df: cudf.DataFrame, max_samples: int = 10000):
    if len(df) > max_samples:
        df = df.sample(n=max_samples)
    return df.reset_index(drop=True)


def send_data_to_api(encoded_df, filename):
    try:
        # Decode the base64 encoded dataframe
        decoded_data = base64.b64decode(encoded_df)
        
        # Create a file-like object from the decoded data
        file_obj = io.BytesIO(decoded_data)
        
        # Send the file to the API
        response = requests.post(
            'http://localhost:8000/load_data',
            files={"file": (filename, file_obj, "application/octet-stream")}
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error loading data into API: {response.text}")
            return False
    except Exception as e:
        print(f"Exception when sending data to API: {str(e)}")
        return False
    
def generate_plot_title(plot_config: Dict[str, Any]) -> str:
    """Generate a descriptive title for the plot based on its configuration."""
    x = plot_config.get('x', 'X')
    y = plot_config.get('y', 'Y')
    title = f"{y} vs {x}"
    
    if plot_config.get('color'):
        title += f", colored by {plot_config['color']}"
    if plot_config.get('size'):
        title += f", size representing {plot_config['size']}"
    
    return title

def parse_and_correct_json(response):
    try:
        # First, try to parse the response as-is
        parsed_json = json_repair.loads(response)
    except json.JSONDecodeError:
        # If JSON is invalid, attempt to extract a JSON-like structure
        json_like = re.search(r'\{.*\}', response, re.DOTALL)
        if json_like:
            try:
                parsed_json = json.loads(json_like.group())
            except json.JSONDecodeError:
                return create_default_structure(response)
        else:
            return create_default_structure(response)

    # Ensure the required keys are present
    if not isinstance(parsed_json, dict):
        parsed_json = {"Sections": [{"Section_Name": "Analysis", "Content": str(parsed_json)}]}
    
    if "Report_Title" not in parsed_json:
        parsed_json["Report_Title"] = "Data Analysis Report"
    
    if "Sections" not in parsed_json:
        parsed_json["Sections"] = [{"Section_Name": "Analysis", "Content": json.dumps(parsed_json)}]
    
    return parsed_json

def create_default_structure(content):
    return {
        "Report_Title": "Data Analysis Report",
        "Sections": [
            {"Section_Name": "Analysis", "Content": content}
        ]
    }
    
def extract_content(content):
    elements = []
    
    # Pattern for code blocks (including nested ones and those with shell markdown)
    code_pattern = r'```(?:shell\s*\n)?markdown\n([\s\S]*?)```'
    
    # Pattern for tables (now including those without leading/trailing pipes)
    table_pattern = r'(\|[^\n]+\|(?:\n\|[-:| ]+\|)?(?:\n[^\n]+\|)+|\n*[^\n\|]+\|[^\n]+(?:\n[-:| ]+\|[-:| ]+)+(?:\n[^\n\|]+\|[^\n]+)+)'
    
    # Split content by code blocks first
    parts = re.split(code_pattern, content)
    
    for i, part in enumerate(parts):
        if i % 2 == 0:  # Not a code block
            # Extract tables
            table_parts = re.split(table_pattern, part)
            for j, table_part in enumerate(table_parts):
                if j % 2 == 0:  # Not a table
                    if table_part.strip():
                        elements.append(('text', table_part.strip()))
                else:  # Table
                    elements.append(('table', table_part.strip()))
        else:  # Code block (potential markdown table)
            # Check if the code block contains a table
            table_match = re.search(table_pattern, part)
            if table_match:
                elements.append(('table', table_match.group(0).strip()))
            else:
                elements.append(('code', part.strip()))
    
    return elements

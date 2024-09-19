import json_repair
import json
import logging
import re
import io
import base64
import requests
import dash_ag_grid as dag
import cudf
import pandas as pd
from .configs import MAX_CACHE_FILES, DATETIME_FORMATS
from pathlib import Path
import asyncio
from dash import html, dcc
import dash_bootstrap_components as dbc
from .formatting_utilities import preprocess_text, create_ag_grid, parse_markdown_table
from .cache_config import cache
from fastapi import HTTPException
from typing import Dict, Any
   
def get_dataframe() -> cudf.DataFrame:
    df = cache.get('current_df')
    if df is None:
        raise HTTPException(status_code=400, detail="No data loaded")
    return df

def extract_table_from_content(content):
    # This function should parse the content and extract any table data
    # You may need to adjust this based on how tables are represented in your content
    table_data = None
    elements = extract_content(content)
    for element_type, element in elements:
        if element_type == 'table':
            table_data = parse_markdown_table(element)
            break
    return table_data

def is_timeseries(df: cudf.DataFrame) -> bool:
    """
    Check if the DataFrame contains any datetime columns.

    Parameters:
    df (cudf.DataFrame): The DataFrame to check.

    Returns:
    bool: True if the DataFrame contains any datetime columns, False otherwise.
    """
    try:
        for col in df.columns:
            if df[col].dtype in DATETIME_FORMATS:
                return True
    except Exception as e:
        print(f"Error checking DataFrame columns: {str(e)}")
    return False

def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()
        
def resample_df(df):
    datetime_cols = df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns.tolist()
    
    for col in datetime_cols:
        freq = df[col].diff().dt.seconds.mode().values[0] / 60
                      
        if freq < 1440:
            # Filter numeric columns for aggregation
            numeric_cols = df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns.tolist()
            agg_dict = {colu: 'mean' for colu in numeric_cols if colu != col}
            
            # Ensure all columns in agg_dict exist in the DataFrame
            for colu in agg_dict.keys():
                if colu not in df.columns:
                    raise ValueError(f"Column '{colu}' specified in aggregation dictionary not found in the DataFrame")

            # Forward-fill categorical columns before resampling
            categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
            df_pandas = df.to_pandas()  # Convert to pandas DataFrame for unsupported operations
            for cat_col in categorical_cols:
                df_pandas[cat_col] = df_pandas[cat_col].ffill()

            # Set the datetime column as the index and resample
            df = cudf.DataFrame.from_pandas(df_pandas)  # Convert back to cudf DataFrame
            df = df.set_index(col)
            resampled = df.resample('D').agg(agg_dict).reset_index()

            # Round all numerical columns to two decimal places
            for colu in resampled.columns:
                if resampled[colu].dtype in ['float64', 'float32']:
                    resampled[colu] = resampled[colu].round(2)

            # Merge forward-filled categorical columns back into the resampled DataFrame
            resampled_pandas = resampled.to_pandas()
            for cat_col in categorical_cols:
                resampled_pandas[cat_col] = df_pandas[cat_col].reindex(resampled_pandas.index, method='ffill')

            return cudf.DataFrame.from_pandas(resampled_pandas)  # Convert back to cudf DataFrame

    return df

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

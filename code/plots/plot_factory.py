import plotly.express as px
import cudf
import json_repair
from utils.configs import llm
from utils.constants import DATETIME_FORMATS
from utils.prompt_templates import generate_plots_prompt
from dash import dcc
import plotly.graph_objects as go
import io
import pandas as pd
from pathlib import Path
import re
from utils.utilities import sample_data, is_timeseries, resample_df , get_dataframe
from typing import Optional, Dict, Any, Tuple
import json
from utils.cache_config import cache

def plot_scatter(df: cudf.DataFrame, x: str, y: str, size: str, color: str = None) -> px.scatter:
    df = df.sort_values(by=[x])  # Add sorting
    df.fillna({x: df[x].mean(), y: df[y].mean(), size: df[size].mean()}, inplace=True)
    fig = px.scatter(df.to_pandas(), x=x, y=y, size=size, color=color)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
    return px.scatter(df.to_pandas(), x=x, y=y, size=size, color=color)


def plot_time_series(df: cudf.DataFrame, x: str, y: str, line_color: str = 'blue', line_dash: str = 'solid', line_width: int = 2) -> go.Figure:
    df = df.sort_values(by=[x])
    
    # Convert to pandas for plotting
    pdf = df.to_pandas()
    
    # Create the plot
    fig = go.Figure()
    
    # Add the main data line with custom color and style
    fig.add_trace(go.Scatter(
        x=pdf[x],
        y=pdf[y],
        mode='lines',
        name='Data',
        line=dict(color=line_color, dash=line_dash, width=line_width)
    ))
    
   
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title=f'{y} over time',
        xaxis_title=x,
        yaxis_title=y,
        showlegend=False,
        xaxis=dict(
            tickformat='%Y-%m-%d',
        )
    )

    fig.add_annotation(
        text="<b>Gaps in Date/Time are filled with Mean for Visualization</b>",
        xref="paper", yref="paper",
        x=0.5, y=1.05,
        yshift=20,
        showarrow=False,
        font=dict(size=12)
    )
    
    return fig

def plot_comparison_bars(df: cudf.DataFrame, x: str, y: str, color: str) -> px.histogram:
    df = df.sort_values(by=[y], ascending=False)  # Sort by y-value descending
    fig = px.histogram(df.to_pandas(), x=x, y=y, color=color, barmode="group")
    fig.update_traces(textposition='outside')
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        uniformtext_minsize=8, 
        uniformtext_mode='hide'
        )
    return fig

def plot_area(df: cudf.DataFrame, x: str, y: str, color: str, line_group: str) -> px.area:
    df = df.sort_values(by=[x])  
    fig = px.area(df.to_pandas(), x=x, y=y, color=color, line_group=line_group)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
    return fig

def plot_violin(df: cudf.DataFrame, x: str, y: str, color: str) -> px.violin:
    fig = px.violin(df.to_pandas(), x=x, y=y, color=color, box=True, points="all")
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
    return fig

def plot_ecdf(df: cudf.DataFrame, x: str, color: str) -> px.ecdf:
    fig = px.ecdf(df.to_pandas(), x=x, color=color, marginal="histogram")
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
    return fig

def plot_parallel_coordinates(df: cudf.DataFrame) -> px.parallel_coordinates:
    fig = px.parallel_coordinates(df.to_pandas(), color="total_bill",
                                   color_continuous_scale=px.colors.diverging.Tealrose,
                                   color_continuous_midpoint=2)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
    return fig

def plot_heatmap(df: cudf.DataFrame) -> px.parallel_coordinates:
    fig = px.imshow(df.to_pandas())
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
    return fig
    
def plot_pie(df: cudf.DataFrame, x: str, y: str) -> px.pie:
    fig = px.pie(df.to_pandas(), values=x, names=y, color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
    return fig

def get_llm_response(df: cudf.DataFrame, section_name: str) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    numerical_cols = df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns.tolist()
    
    if numerical_cols:
        numerical_cols_str = ", ".join(numerical_cols)
    else:
        numerical_cols_str = "None"
    if categorical_cols:
        categorical_cols_str = ", ".join(categorical_cols)
    else:
        categorical_cols_str = "None"
    if datetime_cols:
        datetime_cols_str = ", ".join(datetime_cols)
    else:
        datetime_cols_str = "None"
    
    # Replace placeholders with the corresponding strings
    prompt = generate_plots_prompt.replace("{numerical_columns}", numerical_cols_str)\
                                  .replace("{section_name}", section_name)\
                                  .replace("{categorical_columns}", categorical_cols_str)\
                                  .replace("{datetime_columns}", datetime_cols_str)
    
    return llm.get_response(prompt)

def extract_plot_config(response: str) -> Optional[str]:
    match = re.search(r'\{.*\}', response, re.DOTALL)
    return match.group(0) if match else None

def validate_plot_config(plot_type: str, plot_config: Dict[str, Any]) -> Dict[str, Any]:
    required_params = {
        'scatter': {'x', 'y', 'size', 'color'},
        'bar': {'x', 'y', 'color'},
        'area': {'x', 'y', 'color', 'line_group'},
        'violin': {'x', 'y', 'color'},
        'ecdf': {'x', 'color'},
        'parallelcoordinates': set(),
        'pie': {'x', 'y'},
        'timeseries': {'x', 'y'},
        'heatmap': set()
    }
    
    valid_params = required_params.get(plot_type, set())
    return {k: v for k, v in plot_config.items() if k in valid_params}



async def parse_llm_response(section_name: str, max_samples: int = 10000) -> Tuple[Any, Optional[Dict], Optional[Dict]]:
    df = get_dataframe()
    if is_timeseries(df):
        df = resample_df(df)
    numeric_cols = df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns.tolist()
    for numeric_col in numeric_cols:
        df[numeric_col] = df[numeric_col].fillna(df[numeric_col].mean())
    df = df.drop_duplicates()
        
    if len(df) > max_samples:
        df = df.sample(n=max_samples, random_state=42)  # Use a fixed random state for reproducibility
    
    try:
        response = get_llm_response(df, section_name)  # This is not awaited as it's not an async function
        plot_config_str = extract_plot_config(response)
        if not plot_config_str:
            raise ValueError("No plot configuration found in the response")
        response_dict = json_repair.loads(plot_config_str)  # Changed from response to plot_config_str
    except Exception as e:
        print(f"Error parsing JSON response for {section_name}: {e}")
        return None, None, None

    plot_functions = {
        'scatter': plot_scatter,
        'comparisonbar': plot_comparison_bars,
        'area': plot_area,
        'comparisonviolin': plot_violin,
        'ecdf': plot_ecdf,
        'parallelcoordinates': plot_parallel_coordinates,
        'pie': plot_pie,
        'timeseries': plot_time_series
    }

    try:
        for plot_type, plot_function in plot_functions.items():
            if plot_type in response_dict:
                plot_config = response_dict[plot_type]
                plot_config = validate_plot_config(plot_type, plot_config)
                if plot_type == 'parallelcoordinates':
                    plot = plot_function(df)
                    plot_config = {'type': 'parallelcoordinates'}
                else:
                    plot = plot_function(df, **plot_config)
                
                if plot:
                    plot_data = json.loads(plot.to_json())
                    return plot, plot_data, plot_config
        
        return None, None, None
    except Exception as e:
        print(f"Error generating plot for {section_name}: {str(e)}")
        return None, None, None
from utils.utilities import get_data_from_api, get_dataframe
import pandas as pd
import cudf
import plotly.express as px
import numpy as np
import re
import sys
import io

def remove_show_calls(code):
    """
    Remove all instances of plt.show() and fig.show() from the given code string.

    Args:
        code (str): The input code as a string.

    Returns:
        str: The code string with all plt.show() and fig.show() calls removed.
    """
    show_calls_pattern = re.compile(r'\b(?:plt|fig)\.show\(\s*\)')
    return show_calls_pattern.sub('', code)

def process_response(response):
    """
    Processes a response string containing text, code, and figure segments.
    The function splits the response into segments based on <CODE> and <FIGURE> tags,
    processes each segment, and returns a dictionary with the results.
    Args:
        response (str): The response string to be processed.
    Returns:
        dict: A dictionary with the following structure:
            {
                "results": [
                    {
                        "type": "text" | "code" | "figure" | "error",
                        "content": str | dict,
                        "output": str (only for "code" type)
                    },
                    ...
                ]
            - "type": always "mixed".
            - "results": a list of dictionaries, each representing a processed segment.
                - "type": the type of the segment ("text", "code", "figure", or "error").
                - "content": the content of the segment (text, code, figure, or error message).
                - "output": the output of the executed code (only present for "code" type).
    Raises:
        Exception: If there is an error executing code or creating a figure, the error message
                   is captured and included in the results.
    """
    segments = re.split(r'(<CODE>.*?</CODE>|<FIGURE>.*?</FIGURE>)', response, flags=re.DOTALL)
    df = get_dataframe()
    df = df.to_pandas()
    results = []

    for segment in segments:
        
        segment = remove_show_calls(segment)
        if segment.strip() == "":
            continue
        elif segment.startswith('<CODE>') and segment.endswith('</CODE>'):
            code = segment[6:-7].strip()
            try:
                local_vars = {"pd": pd, "cudf": cudf, "px": px, "df": df, "np": np, "get_data_from_api": get_data_from_api}
                buffer = io.StringIO()
                sys.stdout = buffer
                exec(code, globals(), local_vars)
                sys.stdout = sys.__stdout__
                code_output = buffer.getvalue()
                results.append({"type": "code", "content": code, "output": code_output})
            except Exception as e:
                sys.stdout = sys.__stdout__
                results.append({"type": "error", "content": f"Error executing code: {str(e)}"})
        elif segment.startswith('<FIGURE>') and segment.endswith('</FIGURE>'):
            figure_code = segment[8:-9].strip()
            figure_code = remove_show_calls(figure_code)
            try:
                local_vars = {"pd": pd, "cudf": cudf, "px": px, "df": df, "get_data_from_api": get_data_from_api}
                exec(figure_code, globals(), local_vars)
                if 'fig' in local_vars:
                    results.append({"type": "figure", "content": local_vars['fig']})
                else:
                    results.append({"type": "error", "content": "Figure not created"})
            except Exception as e:
                results.append({"type": "error", "content": f"Error creating figure: {str(e)}"})
        else:
            results.append({"type": "text", "content": segment.strip()})

    return {
        "type": "mixed",
        "results": results,
    }
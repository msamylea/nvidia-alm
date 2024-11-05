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
        code (str): The code string from which to remove show calls.

    Returns:
        str: The code string with all show calls removed.
    """
    show_calls_pattern = re.compile(r'\b(?:plt|fig)\.show\(\s*\)')
    return show_calls_pattern.sub('', code)

def extract_content(tag, segment):
    """
    Extracts the content enclosed within a specified HTML/XML tag from a given text segment.

    Args:
        tag (str): The HTML/XML tag to search for.
        segment (str): The text segment to search within.

    Returns:
        str or None: The content found within the specified tag, with leading and trailing whitespace removed.
                     Returns None if the tag is not found.
    """
    pattern = rf'<{tag}>(.*?)</{tag}>'
    match = re.search(pattern, segment, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    else:
        return None


def process_response(response):
    """
    Processes a response string containing code and figure segments, executes the code, and captures the output.

    Args:
        response (str): The response string containing segments of code and figures wrapped in <CODE> and <FIGURE> tags.

    Returns:
        dict: A dictionary with a "type" key set to "mixed" and a "results" key containing a list of dictionaries. Each dictionary in the list represents a processed segment and has the following structure:
            - For code segments:
                {
                    "type": "code",
                    "content": str,  # The code that was executed
                    "output": str    # The output of the executed code
            - For figure segments:
                {
                    "type": "figure",
                    "content": object  # The figure object created by the code
            - For text segments:
                {
                    "type": "text",
                    "content": str  # The plain text content of the segment
            - For errors:
                {
                    "type": "error",
                    "content": str  # The error message
    """
    segments = re.split(r'(<CODE>.*?</CODE>|<FIGURE>.*?</FIGURE>)', response, flags=re.DOTALL | re.IGNORECASE)
    df = get_dataframe()
    df = df.to_pandas()

    results = []
    context = {}
    last_figure = None

    for segment in segments:
        segment = remove_show_calls(segment)
        if segment.strip() == "":
            continue
        elif re.search(r'<CODE>.*?</CODE>', segment, re.DOTALL | re.IGNORECASE):
            code = extract_content('CODE', segment)
            if code:
                try:
                    local_vars = {"pd": pd, "cudf": cudf, "px": px, "df": df, "np": np, "get_data_from_api": get_data_from_api, **context}
                    buffer = io.StringIO()
                    sys.stdout = buffer
                    exec(code, globals(), local_vars)
                    sys.stdout = sys.__stdout__
                    code_output = buffer.getvalue()
                    if 'fig' in local_vars:
                        results.append({"type": "figure", "content": local_vars['fig']})
                    else:
                        results.append({"type": "code", "content": code, "output": code_output})
                        context.update(local_vars)
                except Exception as e:
                    sys.stdout = sys.__stdout__
                    results.append({"type": "error", "content": f"Error executing code: {str(e)}"})
        elif re.search(r'<FIGURE>.*?</FIGURE>', segment, re.DOTALL | re.IGNORECASE):
            figure_code = extract_content('FIGURE', segment)
            if figure_code:
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
                results.append({"type": "error", "content": "No figure code found"})
        else:
            results.append({"type": "text", "content": segment.strip()})

    return {
        "type": "mixed",
        "results": results,
    }
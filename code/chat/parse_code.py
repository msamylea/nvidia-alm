from utils.utilities import get_data_from_api, get_dataframe
import pandas as pd
import cudf
import plotly.express as px
import numpy as np
import re
import sys
import io

def process_response(response):
    segments = re.split(r'(<CODE>.*?</CODE>|<FIGURE>.*?</FIGURE>)', response, flags=re.DOTALL)
    df = get_dataframe()
    df = df.to_pandas()
    results = []

    for segment in segments:
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
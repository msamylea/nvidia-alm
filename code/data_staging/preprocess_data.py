import sys
from pathlib import Path
import cudf
import numpy as np

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

def prep_data(df: cudf.DataFrame) -> cudf.DataFrame:
    df = handle_duplicates(df)
    df = convert_datetime(df)
    df = handle_missing_values(df)
    
    return df

def handle_duplicates(df: cudf.DataFrame) -> cudf.DataFrame:
    """
    Removes duplicate rows from a cuDF DataFrame.

    Parameters:
    df (cudf.DataFrame): The input DataFrame from which duplicates need to be removed.

    Returns:
    cudf.DataFrame: The DataFrame after removing duplicate rows. If an exception occurs, the original DataFrame is returned.
    """
    try:
        num_duplicates = df.duplicated().sum()
        if num_duplicates > 0:
            df = df.drop_duplicates()
        return df
    except Exception as e:
        return df

def handle_missing_values(df: cudf.DataFrame) -> cudf.DataFrame:
    """
    Handle missing values in a cuDF DataFrame.

    This function fills missing values in the DataFrame based on the data type of each column:
    - For floating point columns, missing values are filled with the mean of the column.
    - For integer columns, missing values are filled with 0.
    - For other data types, missing values are filled with the string "Unknown".

    Args:
        df (cudf.DataFrame): The input cuDF DataFrame with potential missing values.

    Returns:
        cudf.DataFrame: The DataFrame with missing values handled.

    Raises:
        Exception: If an error occurs during the processing, the original DataFrame is returned.
    """
    try:
        for col in df.columns:
            col_dtype = df[col].dtype
            if np.issubdtype(col_dtype, np.floating):
                df[col] = df[col].fillna(df[col].mean())
            elif np.issubdtype(col_dtype, np.integer):
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna("Unknown")

        return df
    except Exception as e:
        return df

def convert_datetime(df: cudf.DataFrame):
    try:
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'year', 'month', 'day', 'datetime']):
                try:
                    df[col] = df[col].str.replace(r'(\+|-)\d{2}:\d{2}$', '', regex=True)
                    df[col] = cudf.to_datetime(df[col])
                except Exception as e:
                    return df
        return df
    except Exception as e:
        return df
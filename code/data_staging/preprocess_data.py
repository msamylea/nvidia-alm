from pathlib import Path
import sys
import cudf
from typing import Tuple
from data_staging.load_data import ingest_data
import numpy as np

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

def prep_data(contents, filename) -> cudf.DataFrame:
    df = ingest_data(contents, filename)
    df, num_duplicates = handle_duplicates(df)
    df, dt_converted = convert_datetime(df)
    df, num_missing = handle_missing_values(df)
    
    return df, num_duplicates, num_missing, dt_converted

    
def handle_duplicates(df: cudf.DataFrame) -> Tuple[cudf.DataFrame, int]:
    try:
        num_duplicates = df.duplicated().sum()
        if num_duplicates > 0:
            df = df.drop_duplicates()
        return df, num_duplicates
    except Exception as e:
        print(f"Error in handle_duplicates: {str(e)}")
        return df, 0

def handle_missing_values(df: cudf.DataFrame) -> Tuple[cudf.DataFrame, int]:
    try:
        num_missing = 0

        for col in df.columns:
            col_dtype = df[col].dtype
            if np.issubdtype(col_dtype, np.floating):
                df[col] = df[col].fillna(df[col].mean())
                num_missing += 1
                print(f"Filled nulls with mean for column: {col}")
            elif np.issubdtype(col_dtype, np.integer):
                df[col] = df[col].fillna(0)
                num_missing += 1
                print(f"Filled nulls with zero for column: {col}")
            else:
                df[col] = df[col].fillna("Unknown")
                num_missing += 1
                print(f"Filled nulls with 'Unknown' for column: {col}")

        return df, num_missing
    except Exception as e:
        print(f"Error in handle_missing_values: {str(e)}")
        import traceback
        traceback.print_exc()
        return df, 0

def convert_datetime(df: cudf.DataFrame) -> Tuple[cudf.DataFrame, int]:
    dt_conv_count = 0
    try:
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                dt_conv_count += 1
            elif any(keyword in col.lower() for keyword in ['date', 'year', 'month', 'day', 'datetime']):
                print("Found potential datetime column", col)
                try:
                    df[col] = df[col].str.replace(r'(\+|-)\d{2}:\d{2}$', '', regex=True)
                    df[col] = cudf.to_datetime(df[col])
                    if df[col].dtype == 'datetime64[ns]':
                        print("Converted column", col, "to datetime")
                        dt_conv_count += 1
                except Exception as e:
                    print(f"Failed to convert column {col}: {e}")
        return df, dt_conv_count
    except Exception as e:
        print(f"Error in convert_datetime: {str(e)}")
        return df, dt_conv_count
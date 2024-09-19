from fastapi import FastAPI, HTTPException, UploadFile, File, Request
import cudf
import io
import os
from fastapi.middleware.cors import CORSMiddleware
from utils.cache_config import cache, cache_key, ClearableCache
from utils.configs import DATETIME_FORMATS, CATEGORICAL_DTYPES
from data_staging.load_data import ingest_data
from data_staging.preprocess_data import prep_data
from utils.utilities import get_dataframe
import traceback
from fastapi import Query
import numpy as np

import sys

def log_info(message):
    print(f"INFO: {message}", flush=True)
    sys.stdout.flush()

def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr, flush=True)
    sys.stderr.flush()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI Root"}

def serialize_value(v):
    if isinstance(v, np.integer):
        return int(v)
    elif isinstance(v, np.floating):
        return float(v)
    elif isinstance(v, np.ndarray):
        return v.tolist()
    return str(v)

@app.post("/load_data")
async def load_data(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        try:
            df = ingest_data(contents, file.filename)
            df, num_duplicates, num_missing, dt_converted = prep_data(df)
        except Exception as e:
            log_info(f"Error loading data: {str(e)}")
        
        
        cache.set('current_df', df)
        
        cached_df = cache.get('current_df')
        if cached_df is not None:
            log_info("Data successfully retrieved from cache.")
            log_info(f"Shape of cached data: {cached_df.shape}")
        else:
            log_info("Data not found in cache.")
        
        return {
            "message": "Data loaded and preprocessed successfully",
            "preprocessing_info": {
                "duplicates_removed": serialize_value(num_duplicates),
                "missing_values_handled": serialize_value(num_missing),
                "datetime_columns_converted": serialize_value(dt_converted)
            },
            "schema": {
                "columns": df.columns.to_list(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            }
        }
    except Exception as e:
        print(f"Error in load_data: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error loading data: {str(e)}")

@app.post("/clear_cache")
async def clear_cache():
    try:
        cache.clear()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        print(f"Error in clear_cache: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")
    
    


@app.get("/schema")
async def get_schema():
    df = get_dataframe()
    return {
        "columns": df.columns.to_list(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "non_null_counts": df.count().to_dict(),
        "sample_values": {col: df[col].head().to_arrow().to_pylist() for col in df.columns}
    }

@app.get("/summary")
async def get_summary():
    df = get_dataframe()
    summary = df.describe().to_pandas().to_dict()
    result = {col: {k: float(v) if isinstance(v, (int, float)) else str(v) for k, v in stats.items()} 
              for col, stats in summary.items()}
    return result
    
@app.get("/sample")
async def get_sample(n: int = 5):
    df = get_dataframe()
    return df.head(n).to_pandas().to_dict(orient="records")

@app.get("/value_counts/{column_name}")
async def get_value_counts(column_name: str, top_n: int = Query(default=10, ge=1)):
    df = get_dataframe()
    if column_name not in df.columns:
        raise HTTPException(status_code=404, detail=f"Column '{column_name}' not found. Available columns are: {', '.join(df.columns)}")
    
    try:
        value_counts = df[column_name].value_counts().head(top_n).to_pandas().to_dict()
        result = {str(k): int(v) for k, v in value_counts.items()}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating value counts: {str(e)}")

@app.get("/column_stats/{column_name}")
async def get_column_stats(column_name: str):
    df = get_dataframe()
    if column_name not in df.columns:
        raise HTTPException(status_code=404, detail=f"Column '{column_name}' not found. Available columns are: {', '.join(df.columns)}")
    
    column_data = df[column_name]
    stats = {
        "mean": float(column_data.mean()) if column_data.dtype in ['int64', 'float64'] else None,
        "median": float(column_data.median()) if column_data.dtype in ['int64', 'float64'] else None,
        "std": float(column_data.std()) if column_data.dtype in ['int64', 'float64'] else None,
        "min": float(column_data.min()) if column_data.dtype in ['int64', 'float64'] else str(column_data.min()),
        "max": float(column_data.max()) if column_data.dtype in ['int64', 'float64'] else str(column_data.max()),
        "unique_values": int(column_data.nunique()),
        "null_count": int(column_data.isnull().sum()),
    }
    return stats

@app.get("/sum_single_column")
async def sum_single_column(column_name: str):
    df = get_dataframe()
    if column_name not in df.columns:
        raise HTTPException(status_code=404, detail=f"Column {column_name} not found")
    
    column_sum = df[column_name].sum()
    return {"sum": float(column_sum)}

@app.get("/outliers/{column_name}")
async def detect_outliers(column_name: str):
    df = get_dataframe()
    if column_name not in df.columns:
        raise HTTPException(status_code=404, detail=f"Column {column_name} not found")
    
    Q1 = df[column_name].quantile(0.25)
    Q3 = df[column_name].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[column_name] < lower_bound) | (df[column_name] > upper_bound)]
    
    return {
        "num_outliers": int(len(outliers)),
        "percentage_outliers": float(len(outliers) / len(df) * 100),
        "outlier_range": {"lower": float(lower_bound), "upper": float(upper_bound)}
    }
    
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path_name: str):
    return {"message": f"You requested {request.method} {path_name}"}
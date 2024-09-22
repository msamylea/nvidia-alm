import io
import cudf

def ingest_data(file_contents, filename) -> cudf.DataFrame:
    file_like_object = io.BytesIO(file_contents)

    if 'csv' in filename.lower():
        try:
           
            df = cudf.read_csv(file_like_object)
        except Exception as e:
            print(f"Error reading CSV file with pandas: {e}")
            try:
                # If pandas fails, try cudf directly
                file_like_object.seek(0)  # Reset file pointer
                df = cudf.read_csv(file_like_object)
            except Exception as e:
                print(f"Error reading CSV file with cudf: {e}")
                return cudf.DataFrame()

    elif 'parquet' in filename.lower() or 'pq' in filename.lower():
        try:
            df = cudf.read_parquet(file_like_object)
        except Exception as e:
            print(f"Error reading Parquet file: {e}")
            return cudf.DataFrame()

    elif 'json' in filename.lower():
        try:
            df = cudf.read_json(file_like_object)
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            return cudf.DataFrame()

    else:
        print("Unsupported file format.")
        return cudf.DataFrame()

    if df.empty:
        print("The resulting DataFrame is empty.")
        return cudf.DataFrame()

    return df
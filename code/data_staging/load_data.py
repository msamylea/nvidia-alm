import io
import cudf
from .preprocess_data import prep_data

def ingest_data(file_contents, filename) -> cudf.DataFrame:
    """
    Ingests data from a file and returns a cuDF DataFrame.
    This function reads data from a file-like object created from the given file contents.
    It supports CSV, Parquet, and JSON file formats. The function attempts to read the file
    using cuDF and preprocesses the data using the `prep_data` function. If reading fails,
    it handles the exceptions and returns an empty DataFrame.
    Args:
        file_contents (bytes): The contents of the file to be ingested.
        filename (str): The name of the file, used to determine the file format.
    Returns:
        cudf.DataFrame: The ingested and preprocessed data as a cuDF DataFrame. 
                        Returns an empty DataFrame if an error occurs or if the file format is unsupported.
    """
    file_like_object = io.BytesIO(file_contents)

    if 'csv' in filename.lower():
        try:
           
            df = cudf.read_csv(file_like_object)
            df = prep_data(df)
        except Exception as e:
            print(f"Error reading CSV file with pandas: {e}")
            try:
                # If pandas fails, try cudf directly
                file_like_object.seek(0)  # Reset file pointer
                df = cudf.read_csv(file_like_object)
                df = prep_data(df)
            except Exception as e:
                print(f"Error reading CSV file with cudf: {e}")
                return cudf.DataFrame()

    elif 'parquet' in filename.lower() or 'pq' in filename.lower():
        try:
            df = cudf.read_parquet(file_like_object)
            df = prep_data(df)
        except Exception as e:
            print(f"Error reading Parquet file: {e}")
            return cudf.DataFrame()

    elif 'json' in filename.lower():
        try:
            df = cudf.read_json(file_like_object)
            df = prep_data(df)
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
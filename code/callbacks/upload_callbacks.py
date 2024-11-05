from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import base64
import traceback
from data_staging.load_data import ingest_data
from utils.cache_config import cache, cache_key
from utils.data_router import get_schema, get_summary

def register_upload_callbacks(app):
    @app.callback(
        Output('stored-data', 'data'),
        Output('output-data-upload', 'children'),
        Output('upload-success', 'is_open'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True   
    )
    def update_output(contents, filename):
        """
        Update the output based on the uploaded file contents.
        Args:
            contents (str): The contents of the uploaded file, encoded in base64.
            filename (str): The name of the uploaded file.
        Returns:
            tuple: A tuple containing:
                - dict: A dictionary with the DataFrame's columns, dtypes, shape, and a reset trigger.
                - str: A message indicating the status of the upload.
                - bool: A boolean indicating the success of the upload.
        Raises:
            PreventUpdate: If the contents are None.
        """
        if contents is None:
            raise PreventUpdate

        print(f"Processing uploaded file: {filename}")  # Debug logging
        
        try:
            # Clear the cache before processing new data
            cache.clear()
            print("Cache cleared successfully")  # Debug logging
            
            # Decode and process the file contents
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            print("Ingesting data...")  # Debug logging
            df = ingest_data(decoded, filename)
            
            if df is not None:
                try:
                    print(f"Data ingested successfully. Shape: {df.shape}")  # Debug logging
                    
                    stored_data = {
                        'columns': df.columns.tolist(),
                        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                        'shape': list(df.shape),
                        'reset_trigger': True
                    }
                    
                    print("Setting data in cache...")  # Debug logging
                    cache.set('current_df', df)
                    
                    # Update cache with new schema and summary
                    print("Fetching and caching schema...")  # Debug logging
                    new_schema = get_schema()
                    print("Fetching and caching summary...")  # Debug logging
                    new_summary = get_summary()
                    
                    cache.set(cache_key("get_schema"), new_schema)
                    cache.set(cache_key("get_summary"), new_summary)
                    
                    print("Data processing completed successfully")  # Debug logging
                    return stored_data, f"Data uploaded successfully: {filename}", True
                    
                except Exception as e:
                    print(f"Error processing data: {str(e)}")  # Debug logging
                    print(traceback.format_exc())  # Print full traceback
                    return None, f"Error processing data: {str(e)}", False
            else:
                print("Error: ingest_data returned None")  # Debug logging
                return None, "Error loading data: Data ingestion failed", False
                
        except Exception as e:
            print(f"Error in file upload: {str(e)}")  # Debug logging
            print(traceback.format_exc())  # Print full traceback
            return None, f"Error processing file: {str(e)}", False
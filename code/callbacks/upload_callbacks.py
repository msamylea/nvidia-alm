from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import base64
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
        try:
            cache.clear()
            
            # Decode and process the file contents
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            df = ingest_data(decoded, filename)
            if df is not None:
                try:
                    stored_data = {
                        'columns': df.columns.tolist(),
                        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                        'shape': list(df.shape),
                        'reset_trigger': True
                    }
                    
                    cache.set('current_df', df)
                    
                    # Update cache with new schema and summary
                    new_schema = get_schema()
                    new_summary = get_summary()
                    cache.set(cache_key("get_schema"), new_schema)
                    cache.set(cache_key("get_summary"), new_summary)
                    
                    return stored_data, f"Data uploaded: {filename}", True
                except Exception as e:
                    print(f"Error processing file: {str(e)}")
                    return None, f"Error processing file: {str(e)}", False
            else:
                return None, "Error loading data", False
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return None, f"Error processing file: {str(e)}", False
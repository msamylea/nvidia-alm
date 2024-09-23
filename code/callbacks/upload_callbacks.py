from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import base64
from data_staging.load_data import ingest_data
from utils.cache_config import cache

def register_upload_callbacks(app):
    @app.callback(
        Output('stored-data', 'data'),
        Output('output-data-upload', 'children'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True   
    )
    def update_output(contents, filename):
        if contents is None:
            raise PreventUpdate
        try:
            cache.clear()
            
            # Decode the file contents
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Load data and process it
            df = ingest_data(decoded, filename)
            if df is not None:
                # Store DataFrame info
                stored_data = {
                    'columns': df.columns.tolist(),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'shape': list(df.shape),
                    'reset_trigger': True
                }
                # Store the DataFrame in cache
                cache.set('current_df', df)
                return stored_data, f"Data uploaded: {filename}"
            else:
                return None, "Error loading data"
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return None, f"Error processing file: {str(e)}"
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import base64
from data_staging.load_data import ingest_data
from utils.utilities import send_data_to_api
from utils.cache_config import cache
import json
import numpy as np

def register_upload_callbacks(app):
    @app.callback(
        Output('stored-data', 'data'),
        Output('output-data-upload', 'children'),
        Output('file-indicator', 'value'),
        Output('file-indicator', 'color'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
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
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},  # Convert dtypes to strings
                    'shape': list(df.shape),  # Convert shape to a list
                    'reset_trigger': True
                }
                # Store the DataFrame in cache
                cache.set('current_df', df)
                return stored_data, f"{filename} uploaded and processed successfully", True, 'green'
            else:
                return None, "Error loading data", False, 'red'
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return None, f"There was an error processing the file: {str(e)}", False, 'red'
        
    @app.callback(
        Output('llm-submit-prompt', 'disabled'),
        Input('stored-data', 'data'),
        Input('tabs', 'active_tab')
    )
    def update_llm_submit_button(stored_data, active_tab):
        if active_tab != 'home':
            raise PreventUpdate
        return stored_data is None
    
    @app.callback(
    Output('target-column', 'options'),
    Output('feature-column', 'options'),
    Input('stored-data', 'data'),
    Input('tabs', 'active_tab'),
    Input('model-type', 'value')
    )
    def update_prediction_dropdowns(stored_data, active_tab, model_type):
        if active_tab != 'predictions' or stored_data is None:
            raise PreventUpdate
        
        columns = stored_data.get('columns', [])
        dtypes = stored_data.get('dtypes', {})
        
        target_options = [
            {'label': col, 'value': col, 'categorical': dtypes.get(col) == 'object'}
            for col in columns
        ]
        
        feature_options = [{'label': col, 'value': col} for col in columns]
        
        return target_options, feature_options
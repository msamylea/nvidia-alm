import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
from dash import callback_context as ctx
import dash
from dash.exceptions import PreventUpdate
from utils.utilities import get_dataframe
from utils.constants import DATETIME_FORMATS, MODEL_CHOICES_OPTIONS
import base64
import io
import cudf.pandas
cudf.pandas.install()
import cupy as cp
import gc
import pandas as pd

prediction_content = html.Div([
    dcc.Store(id='mse-store'),
    dcc.Store(id='mae-store'),
    dcc.Store(id='r2-store'),
    dcc.Store(id='msle-store'),
    dcc.Store(id='accuracy-store'),
    dcc.Store(id='precision-store'),
    dcc.Store(id='recall-store'),
    dcc.Store(id='f1-store'),
    html.Hr(),
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Predictive Analytics", className="info-box-heading"),
                            html.P("Use to view possible trends and events.", className='info-box-text'),
                            
                            dbc.Row([
                                dbc.Col(html.Label("Target Column:"), width=3, style={'text-align': 'left', 'font-weight': 'bold'}),
                                dbc.Col(dbc.Select(id="target-column", placeholder="Select target to predict...", style={'width': '100%', 'backgroundColor': 'white', 'margin-right': '10px'}), width=9),
                            ]),
                            html.Br(),
                            
                            dbc.Row([
                                dbc.Col(html.Label("Feature Column:"), width=3, style={'text-align': 'left', 'font-weight': 'bold'}),
                                dbc.Col(dbc.Select(id="feature-column", placeholder="Select feature to use to create prediction (if timeseries, this is often the date)...", style={'width': '100%', 'backgroundColor': 'white', 'margin-right': '10px'}), width=9),
                            ]),
                            html.Br(),
                            
                            dbc.Row([
                                dbc.Col(html.Label("Select Model:"), width=3, style={'text-align': 'left', 'font-weight': 'bold'}),
                                dbc.Col(dbc.Select(id="model-type", options=MODEL_CHOICES_OPTIONS, placeholder="Select model to use for prediction...", style={'width': '100%', 'backgroundColor': 'white', 'margin-right': '10px'}), width=9),    
                            ]),
                            html.Br(),
                            
                            dbc.Row([
                                dbc.Col(html.Label("Periods to Predict:"), width=3, style={'text-align': 'left', 'font-weight': 'bold'}),
                                dbc.Col(dbc.Input(id="periods-to-predict", type="number", placeholder="Enter number of predictions to generate...", style={'width': '100%', 'backgroundColor': 'white', 'margin-right': '10px'}), width=9),
                            ], id="periods-row", style={'display': 'none'}),
                            html.Br(),
                            
                            dbc.Row([
                                dbc.Col(width=3),  # Empty column for alignment
                                dbc.Col(dbc.Button("Generate Prediction", id="generate-prediction", color="primary", className="custom-btn"), width=9),
                            ]),
                            dbc.Alert(id="error-message", color="danger", is_open=False, dismissable=True, style={'margin-top': '10px'}),
                        ])
                    ], className="info-box"),
                ], width=6),
                
                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Model Metrics", className="info-box-heading"),
                        html.Br(),
                        html.Div([
                            html.H5("Regression Metrics", className="mt-3"),
                            dbc.Row([
                                dbc.Col([html.Strong("Metric")], width=4),
                                dbc.Col([html.Strong("Value")], width=2),
                                dbc.Col([html.Strong("Range")], width=6),
                            ]),
                            html.Hr(style={'margin': '10px 0'}),
                            dbc.Row([
                                dbc.Col([html.Span("Mean Squared Error (MSE)")], width=4, style={'text-align': 'left'}),
                                dbc.Col([html.Span(id="mse-value")], width=2),
                                dbc.Col([html.Span("0 to ∞, lower is better")], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([html.Span("Mean Absolute Error (MAE)")], width=4, style={'text-align': 'left'}),
                                dbc.Col([html.Span(id="mae-value")], width=2),
                                dbc.Col([html.Span("0 to ∞, lower is better")], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([html.Span("R-squared (R²)")], width=4, style={'text-align': 'left'}),
                                dbc.Col([html.Span(id="r2-value")], width=2),
                                dbc.Col([html.Span("0 to 1, higher is better")], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([html.Span("Mean Squared Log Error (MSLE)")], width=4, style={'text-align': 'left'}),
                                dbc.Col([html.Span(id="msle-value")], width=2),
                                dbc.Col([html.Span("0 to ∞, lower is better")], width=6),
                            ]),
                        ], id="regression-metrics"),
                        html.Div([
                            html.H5("Classification Metrics", className="mt-3"),
                            dbc.Row([
                                dbc.Col([html.Strong("Metric")], width=4),
                                dbc.Col([html.Strong("Value")], width=2),
                                dbc.Col([html.Strong("Range")], width=6),
                            ]),
                            html.Hr(style={'margin': '10px 0'}),
                            dbc.Row([
                                dbc.Col([html.Span("Accuracy")], width=4, style={'text-align': 'left'}),
                                dbc.Col([html.Span(id="accuracy-value")], width=2),
                                dbc.Col([html.Span("0 to 1, higher is better")], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([html.Span("Precision")], width=4, style={'text-align': 'left'}),
                                dbc.Col([html.Span(id="precision-value")], width=2),
                                dbc.Col([html.Span("0 to 1, higher is better")], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([html.Span("Recall")], width=4, style={'text-align': 'left'}),
                                dbc.Col([html.Span(id="recall-value")], width=2),
                                dbc.Col([html.Span("0 to 1, higher is better")], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([html.Span("F1 Score")], width=4, style={'text-align': 'left'}),
                                dbc.Col([html.Span(id="f1-value")], width=2),
                                dbc.Col([html.Span("0 to 1, higher is better")], width=6),
                            ]),
                        ], id="classification-metrics"),
                    ])
                ], className="info-box"),
            ], width=6),
            ]),
        ])
    ]),
    
    dcc.Loading(
        html.Div(id="model-prediction", className="mt-4"),
        target_components={"model-prediction": "children"}
    ),
    html.Div(id="prediction-table", className="mt-4"),
    html.Br(),
    dcc.Store(id='mse-store'),
    dcc.Store(id='mae-store'),
    dcc.Store(id='r2-store'),
    dcc.Store(id='msle-store'),
], id="page-content")

def free_gpu_memory():
    cp.get_default_memory_pool().free_all_blocks()
    cp.get_default_pinned_memory_pool().free_all_blocks()
    gc.collect()

@callback(
    Output('periods-row', 'style'),
    Output('error-message', 'children', allow_duplicate=True),
    Input('model-type', 'value'),
    Input('feature-column', 'value'),
    Input('target-column', 'value'),
    State('stored-data', 'data'),
    prevent_initial_call=True
)
def update_periods_visibility_and_check_datetime(model_type, feature_column, target_column, stored_data):
    if stored_data is None:
        return {'display': 'none'}, 'No data uploaded'

    if not model_type or not feature_column or not target_column:
        return {'display': 'none'}, ''

    try:
        df = get_dataframe()
        
        if feature_column not in df.columns or target_column not in df.columns:
            return {'display': 'none'}, 'Selected columns not found in current dataset'

        if model_type == "es":  # Exponential Smoothing
            if df[feature_column].dtype in DATETIME_FORMATS:
                return {'display': 'block'}, ''
            else:
                return {'display': 'none'}, f"Error: Selected feature column '{feature_column}' is not a datetime column."
        
        return {'display': 'none'}, ''
    finally:
        free_gpu_memory()

@callback(
    Output('generate-prediction', 'disabled'),
    Input('target-column', 'value'),
    Input('feature-column', 'value'),
    Input('model-type', 'value'),   
    Input('periods-to-predict', 'value'),
    State('stored-data', 'data')
)
def update_generate_prediction_button(target, feature, model, periods, stored_data):
    if stored_data is None or not all([target, feature, model]):
        return True
    
    try:
        df = get_dataframe()
        
        if target not in df.columns or feature not in df.columns:
            return True
        
        if model == "es":  # Exponential Smoothing
            return not periods or df[feature].dtype not in DATETIME_FORMATS
        else:
            return False
    finally:
        del df
        free_gpu_memory()

@callback(
    Output('target-column', 'value', allow_duplicate=True),
    Output('feature-column', 'value'),
    Output('model-type', 'value'),
    Output('error-message', 'children', allow_duplicate=True),
    Output('error-message', 'is_open', allow_duplicate=True),
    Input('stored-data', 'data'),
    Input('tabs', 'active_tab'),
    Input('target-column', 'value'),
    Input('model-type', 'value'),
    State('target-column', 'options'),
    prevent_initial_call=True
)
def reset_and_validate_inputs(stored_data, active_tab, target_column, model_type, target_options):
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'stored-data' or triggered_id == 'tabs':
        if active_tab != 'predictions' or stored_data is None:
            raise PreventUpdate
        if stored_data.get('reset_trigger', False):
            stored_data['reset_trigger'] = False
            free_gpu_memory()
            return None, None, None, dash.no_update, False
    
    elif triggered_id in ['target-column', 'model-type']:
        if not target_column or not model_type:
            return target_column, dash.no_update, dash.no_update, dash.no_update, False
        
        target_info = next((opt for opt in target_options if opt['value'] == target_column), None)
        if not target_info:
            return None, dash.no_update, dash.no_update, "Invalid target column selected.", True
        
        is_categorical = target_info['categorical']
        
        if is_categorical and model_type != 'rf':
            return None, dash.no_update, dash.no_update, "Categorical target is only allowed for Random Forest model.", True
            
        return target_column, dash.no_update, dash.no_update, dash.no_update, False
    
    raise PreventUpdate
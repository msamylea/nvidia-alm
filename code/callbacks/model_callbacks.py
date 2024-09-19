from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
import base64
import io
import pandas as pd
import numpy as np
import cudf
import cupy as cp
from cuml_models.e_smoothing import make_timeseries_prediction
from cuml_models.regression import make_prediction
from cuml_models.random_forest import make_rf_prediction
from plots.pred_model_plot import plot_regression_vs_actual, plot_timeseries_vs_actual, plot_confusion_matrix
from utils.constants import DATETIME_FORMATS
from utils.utilities import get_dataframe

def register_model_callbacks(app):
    @app.callback(
        Output('model-prediction', 'children'),
        Output('model-prediction', 'style'),
        Output('prediction-table', 'children'),
        Output('mse-store', 'data'),
        Output('mae-store', 'data'),
        Output('r2-store', 'data'),
        Output('msle-store', 'data'),
        Output('accuracy-store', 'data'),
        Output('precision-store', 'data'),
        Output('recall-store', 'data'),
        Output('f1-store', 'data'),
        Input('generate-prediction', 'n_clicks'),
        State('stored-data', 'data'),
        State('target-column', 'value'),
        State('feature-column', 'value'),
        State('periods-to-predict', 'value'),
        State('model-type', 'value'),
        State('error-message', 'children'),
        prevent_initial_call=True
    )
    def generate_prediction(n_clicks, stored_data, target_column, feature_column, periods_to_predict, model_type, error_message):
        if n_clicks is None or stored_data is None:
            raise PreventUpdate
        
        if error_message:
            return error_message, {"display": "block"}, None, None, None, None, None, None, None, None, None

        try:
            df = get_dataframe()            
            
          
            if model_type == "es":  # Exponential Smoothing
                periods_to_predict = int(periods_to_predict)
            
            feature_col = None
            for col in df.columns:
                if feature_column.lower() in col.lower():
                    feature_col = col
                    break

            if feature_col is None:
                return html.Div("Feature column not found in DataFrame."), {"display": "block"}, None, None, None, None, None
            
            is_datetime = df[feature_col].dtype in DATETIME_FORMATS

            try:
                if model_type == "es":  # Exponential Smoothing
                    if not is_datetime:
                        return html.Div("Exponential Smoothing requires a datetime feature column."), {"display": "block"}, None, None, None, None, None, None, None, None, None
                    past_df, future_df, mse, mae, r2, msle = make_timeseries_prediction(df, target_column, feature_column, periods_to_predict)
                    past_df.dropna(inplace=True)
                    fig = plot_timeseries_vs_actual(past_df, future_df, target_column)
                    combined_df = cudf.concat([past_df, future_df])
                    table = create_aggrid_timeseries(combined_df)
                    return dcc.Graph(figure=fig), {"display": "block"}, table, mse, mae, r2, msle, None, None, None, None
                elif model_type == "rf":  # Random Forest
                    result = make_rf_prediction(df, target_column, feature_col)
                    if result is None or len(result) != 8:
                        raise ValueError("Unexpected result from make_rf_prediction")
                    future_df, feature_col, target_column, metric1, metric2, metric3, metric4, is_classification = result
                    df.dropna(inplace=True)
                    future_df.dropna(inplace=True)
                    if is_classification:
                        fig = plot_confusion_matrix(df[target_column], future_df[target_column])
                        table = create_aggrid_regression(future_df)
                        return dcc.Graph(figure=fig), {"display": "block"}, table, None, None, None, None, metric1, metric2, metric3, metric4
                    else:
                        fig = plot_regression_vs_actual(df, feature_col, target_column, future_df)
                        table = create_aggrid_regression(future_df)
                        return dcc.Graph(figure=fig), {"display": "block"}, table, metric1, metric2, metric3, metric4, None, None, None, None
                elif model_type == "lr":  # Linear Regression
                    future_df, feature_col, target_column, mse, mae, r2, msle = make_prediction(df, target_column, feature_col)
                    df.dropna(inplace=True)
                    future_df.dropna(inplace=True)
                    fig = plot_regression_vs_actual(df, feature_col, target_column, future_df)
                    table = create_aggrid_regression(future_df)
                    return dcc.Graph(figure=fig), {"display": "block"}, table, mse, mae, r2, msle, None, None, None, None
                else:
                    return html.Div(f"Unsupported model type: {model_type}"), {"display": "block"}, None, None, None, None, None
                    

            except Exception as e:
                print(f"Error in prediction or plotting: {str(e)}")
                return html.Div(f"Error in prediction or plotting: {str(e)}"), {"display": "block"}, None, None, None, None, None

        except Exception as e:
            print(f"Error in generate_prediction: {str(e)}")
            return html.Div(f"Error in generate_prediction: {str(e)}"), {"display": "block"}, None, None, None, None, None, None, None, None, None

        
    def create_aggrid_timeseries(combined_df):

        return dag.AgGrid(
            rowData=combined_df.reset_index().to_dict('records'),
            columnDefs=[
                    {'field': i, 'valueFormatter': {"function": "d3.format('(.6f')(params.value)"}} if i not in ["datetime", "index", "Datetime"] else {'field': i}
                    for i in combined_df.reset_index().columns
                ],
            className="ag-theme-alpine-dark",
            columnSize="sizeToFit",
        )
        
    def create_aggrid_regression(future_df):
        
        # Ensure that the DataFrame is converted to a dictionary correctly
        row_data = future_df.to_pandas().to_dict('records')
         
        # Convert unsupported data types to supported ones
        supported_dtypes = ['float32', 'float64', 'int32', 'int64']
        for col in future_df.columns:
            if future_df[col].dtype not in supported_dtypes:
                if 'float' in str(future_df[col].dtype):
                    future_df[col] = future_df[col].astype('float64')
                elif 'int' in str(future_df[col].dtype):
                    future_df[col] = future_df[col].astype('int64')
                else:
                    future_df[col] = future_df[col].astype('object')
        
        # Dynamically create column definitions
        column_defs = []
        for col in future_df.columns:
            col_def = {'field': col, 'headerName': col}
            if future_df[col].dtype in ['float64', 'float32']:
                col_def['valueFormatter'] = {"function": "d3.format('(.6f')(params.value)"}
            column_defs.append(col_def)
        
        return dag.AgGrid(
            rowData=row_data,
            columnDefs=column_defs,
            className="ag-theme-alpine-dark",
            columnSize="sizeToFit",
        )
        
    @app.callback(
    Output('mse-value', 'children'),
    Output('mae-value', 'children'),
    Output('r2-value', 'children'),
    Output('msle-value', 'children'),
    Output('accuracy-value', 'children'),
    Output('precision-value', 'children'),
    Output('recall-value', 'children'),
    Output('f1-value', 'children'),
    Output('regression-metrics', 'style'),
    Output('classification-metrics', 'style'),
    Input('mse-store', 'data'),
    Input('mae-store', 'data'),
    Input('r2-store', 'data'),
    Input('msle-store', 'data'),
    Input('accuracy-store', 'data'),
    Input('precision-store', 'data'),
    Input('recall-store', 'data'),
    Input('f1-store', 'data'),
    Input('model-type', 'value')
)
    def update_metrics(mse, mae, r2, msle, accuracy, precision, recall, f1, model_type):
        if model_type is None:
            raise PreventUpdate
        
        def format_metric(value):
            return f"{value:.8f}" if value is not None else "N/A"
        
        if model_type in ['es', 'lr'] or (model_type == 'rf' and mse is not None):  # Regression models
            return (
                format_metric(mse),
                format_metric(mae),
                format_metric(r2),
                format_metric(msle),
                "N/A", "N/A", "N/A", "N/A",  # Classification metrics
                {'display': 'block'},  # Show regression metrics
                {'display': 'none'}  # Hide classification metrics
            )
        elif model_type == 'rf' and accuracy is not None:  # Classification
            return (
                "N/A", "N/A", "N/A", "N/A",
                format_metric(accuracy),
                format_metric(precision),
                format_metric(recall),
                format_metric(f1),
                {'display': 'none'},
                {'display': 'block'}
            )
        else:
            # No prediction made yet
            return (
                "N/A", "N/A", "N/A", "N/A",
                "N/A", "N/A", "N/A", "N/A",
                {'display': 'none'},
                {'display': 'none'}
            )
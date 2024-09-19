import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import cudf
import pandas as pd
from cuml.preprocessing import LabelEncoder
from cuml_models.metrics import get_confusion_matrix
import cupy as cp
from cudf import Series, DataFrame

def plot_timeseries_vs_actual(past_df, future_df, target_column):
    
    try:
        past_df_pd = past_df.to_pandas()
        future_df_pd = future_df.to_pandas()
    except Exception as e:
        print(f"Error converting past and future DataFrames to pandas: {str(e)}")
        return None
    
    # Create a plotly figure
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    
    # Add actual data
    fig.add_trace(go.Scatter(x=past_df_pd.index, y=past_df_pd[target_column], 
                             mode='lines', name='Actual', line=dict(color='blue')))
    
    # Add past predictions
    fig.add_trace(go.Scatter(x=past_df_pd.index, y=past_df_pd['Prediction'], 
                             mode='lines', name='Past Predictions', line=dict(color='green')))
    
    # Add future predictions
    fig.add_trace(go.Scatter(x=future_df_pd.index, y=future_df_pd['Prediction'], 
                             mode='lines', name='Future Predictions', line=dict(color='red')))
    
    # Update layout
    fig.update_layout(
        title=f'Predictions vs Actual)',
        xaxis_title='Date',
        yaxis_title=target_column,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
    
    return fig


def plot_regression_vs_actual(df, feature_column, target_column, future_df):
    try:
        # Convert to pandas if needed
        if isinstance(df, cudf.DataFrame):
            df = df.to_pandas()
        if isinstance(future_df, cudf.DataFrame):
            future_df = future_df.to_pandas()
        
        # Check for empty dataframes
        if df.empty or future_df.empty:
            print("One or both dataframes are empty")
            return None

        # Determine the bar width dynamically based on the number of data points
        num_points = max(len(df), len(future_df))
        bar_width = max(0.8 / num_points, 0.01)  # Ensure a minimum width

        # Create traces
        actual_trace = go.Bar(
            x=df[feature_column],
            y=df[target_column],
            name='Actual Data',
            marker_color='darkblue',
            width=bar_width
        )

        predicted_trace = go.Bar(
            x=future_df[feature_column],
            y=future_df[target_column],
            name='Predicted Data',
            marker_color='darkred',
            width=bar_width
        )

        # Combine traces
        data = [actual_trace, predicted_trace]

        layout = go.Layout(
            title=f'{target_column} vs {feature_column}',
            xaxis=dict(title=feature_column),
            yaxis=dict(title=target_column),
            barmode='group',
            legend=dict(x=0, y=1, traceorder='normal')
        )

        # Create figure
        fig = go.Figure(data=data, layout=layout)

        # Convert columns to numeric types
        df[target_column] = pd.to_numeric(df[target_column], errors='coerce')
        future_df[target_column] = pd.to_numeric(future_df[target_column], errors='coerce')

        # Update y-axis to start from 0 if all values are positive
        if all(df[target_column] >= 0) and all(future_df[target_column] >= 0):
            fig.update_yaxes(rangemode="tozero")

        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        
        return fig
    
    except Exception as e:
        print(f"Error in plot_regression_vs_actual: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def plot_confusion_matrix(y_true, y_pred):
    try:
        # Convert to cuDF Series if they are not already
        if not isinstance(y_true, Series):
            y_true = Series(y_true)
        if not isinstance(y_pred, Series):
            y_pred = Series(y_pred)

        # Handle string labels
        if y_true.dtype == 'object':
            le = LabelEncoder()
            y_true = le.fit_transform(y_true)
            y_pred = le.transform(y_pred)
            class_names = le.classes_.to_pandas().to_list()
        else:
            # Combine y_true and y_pred to get all possible classes
            combined = cp.concatenate((y_true.to_cupy(), y_pred.to_cupy()))
            class_names = cp.unique(combined).get().tolist()

        # Compute the confusion matrix using the provided function
        matrix = get_confusion_matrix(y_true, y_pred)

        # If the number of class names doesn't match the matrix dimensions,
        # adjust the class names to match the matrix
        if len(class_names) != matrix.shape[0]:
            print(f"Warning: Number of class names ({len(class_names)}) doesn't match the confusion matrix dimensions ({matrix.shape[0]})")
            print("Adjusting class names to match matrix dimensions...")
            class_names = [str(i) for i in range(matrix.shape[0])]

        # Convert matrix to numpy array for plotting
        matrix_np = matrix.get()
        
        fig = go.Figure(data=go.Heatmap(
                        z=matrix_np,
                        x=class_names,
                        y=class_names,
                        colorscale='Viridis'))

        fig.update_layout(
            title='Confusion Matrix',
            xaxis_title='Predicted label',
            yaxis_title='True label'
        )

        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })

        return fig

    except Exception as e:
        print(f"Error in plot_confusion_matrix: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
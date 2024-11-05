from utils.fuzzy_matching import apply_fuzzy_matching
import cudf
import plotly.express as px
import plotly.graph_objects as go
import cupy as cp
from cuml.model_selection import train_test_split
from cuml.linear_model import LinearRegression


@apply_fuzzy_matching('x', 'y', 'size', 'color')
def plot_scatter(df: cudf.DataFrame, x: str, y: str, size: str, color: str = None) -> px.scatter:
    """
    Generates a scatter plot using Plotly Express from a cuDF DataFrame.

    Parameters:
    df (cudf.DataFrame): The input DataFrame containing the data to plot.
    x (str): The column name to be used for the x-axis.
    y (str): The column name to be used for the y-axis.
    size (str): The column name to be used for the size of the markers.
    color (str, optional): The column name to be used for the color of the markers. Defaults to None.

    Returns:
    px.scatter: A Plotly Express scatter plot figure object.

    Notes:
    - The DataFrame is sorted by the x column before plotting.
    - Missing values in the x, y, and size columns are filled with the mean of their respective columns.
    - The background of the plot and paper is set to be transparent.
    """
    df = df.sort_values(by=[x])  # Add sorting
    df.fillna({x: df[x].mean(), y: df[y].mean(), size: df[size].mean()}, inplace=True)
    fig = px.scatter(df.to_pandas(), x=x, y=y, size=size, color=color)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig

@apply_fuzzy_matching('x', 'y')
def plot_time_series(df: cudf.DataFrame, x: str, y: str, line_color: str = 'blue', line_dash: str = 'solid', line_width: int = 2) -> go.Figure:
    """
    Generates a time series plot using Plotly for the given DataFrame.
    Parameters:
    df (cudf.DataFrame): The input DataFrame containing the data to plot.
    x (str): The column name to be used for the x-axis.
    y (str): The column name to be used for the y-axis.
    line_color (str, optional): The color of the line in the plot. Default is 'blue'.
    line_dash (str, optional): The dash style of the line in the plot. Default is 'solid'.
    line_width (int, optional): The width of the line in the plot. Default is 2.
    Returns:
    go.Figure: A Plotly Figure object representing the time series plot.
    Notes:
    - The DataFrame is sorted by the x column before plotting.
    - The DataFrame is converted to a pandas DataFrame for compatibility with Plotly.
    - An annotation is added to the plot indicating that gaps in date/time are filled with mean for visualization.
    """
    if x not in df.columns:
        return
    if y not in df.columns:
        return
    
    df = df.sort_values(by=[x])
    pdf = df.to_pandas()
    
    # Create the plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=pdf[x],
        y=pdf[y],
        mode='lines',
        name='Data',
        line=dict(color=line_color, dash=line_dash, width=line_width)
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title=f'{y} over time',
        xaxis_title=x,
        yaxis_title=y,
        showlegend=False,
        xaxis=dict(
            tickformat='%Y-%m-%d',
        )
    )

    fig.add_annotation(
        text="<b>Gaps in Date/Time are filled with Mean for Visualization</b>",
        xref="paper", yref="paper",
        x=0.5, y=1.05,
        yshift=20,
        showarrow=False,
        font=dict(size=12)
    )
    
    return fig

@apply_fuzzy_matching('x', 'y', 'color')
def plot_comparison_bars(df: cudf.DataFrame, x: str, y: str, color: str) -> px.histogram:
    """
    Generate a grouped bar plot for comparison using Plotly.

    Parameters:
    df (cudf.DataFrame): The input dataframe containing the data to plot.
    x (str): The column name to be used for the x-axis.
    y (str): The column name to be used for the y-axis.
    color (str): The column name to be used for coloring the bars.

    Returns:
    px.histogram: A Plotly histogram figure object with the grouped bar plot.
    """
    df = df.sort_values(by=[y], ascending=False)  # Sort by y-value descending
    fig = px.histogram(df.to_pandas(), x=x, y=y, color=color, barmode="group")
    fig.update_traces(textposition='outside')
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        uniformtext_minsize=8, 
        uniformtext_mode='hide'
    )
    return fig

@apply_fuzzy_matching('x', 'y')
def plot_linear_regression(df: cudf.DataFrame, x: str, y: str, test_size: float = 0.2) -> go.Figure:
    """
    Generates a linear regression plot using the provided DataFrame and specified columns.
    Parameters:
    df (cudf.DataFrame): The input DataFrame containing the data.
    x (str): The name of the column to be used as the independent variable.
    y (str): The name of the column to be used as the dependent variable.
    test_size (float, optional): The proportion of the dataset to include in the test split. Default is 0.2.
    Returns:
    go.Figure: A Plotly Figure object containing the linear regression plot. Returns None if an error occurs or if required columns are missing.
    """
    try:
        df = df.sort_values(by=[x])
        
        # Check if all required columns are present
        required_columns = [x, y]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None

        # Split the data into training and testing sets
        X = df[x].values.reshape(-1, 1)
        y = df[y].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

        # Train the linear regression model
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        y_pred = lr.predict(X_test)

        # Convert to CuPy arrays
        X_test = cp.asarray(X_test)
        y_test = cp.asarray(y_test)
        y_pred = cp.asarray(y_pred)

        # Convert CuPy arrays to NumPy arrays for plotting
        X_test_np = X_test.get()
        y_test_np = y_test.get()
        y_pred_np = y_pred.get()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=X_test_np.flatten(), y=y_test_np, mode='markers', name='Actual'))
        fig.add_trace(go.Scatter(x=X_test_np.flatten(), y=y_pred_np, mode='lines', name='Predicted'))
        
        fig.update_layout({
            'title': f'Linear Regression: {y} ~ {x}',
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })

        return fig
    except Exception as e:
        return None
    
@apply_fuzzy_matching('x', 'y', 'color')
def plot_violin(df: cudf.DataFrame, x: str, y: str, color: str) -> px.violin:
    """
    Generates a violin plot using the given DataFrame and specified columns.

    Parameters:
    df (cudf.DataFrame): The input DataFrame containing the data to plot.
    x (str): The column name to be used for the x-axis.
    y (str): The column name to be used for the y-axis.
    color (str): The column name to be used for coloring the violins.

    Returns:
    px.violin: A Plotly Express violin plot object.
    """
    fig = px.violin(df.to_pandas(), x=x, y=y, color=color, box=True, points="all")
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig

@apply_fuzzy_matching('x', 'color')
def plot_ecdf(df: cudf.DataFrame, x: str, color: str) -> px.ecdf:
    """
    Generates an Empirical Cumulative Distribution Function (ECDF) plot using Plotly.

    Parameters:
    df (cudf.DataFrame): The input dataframe containing the data to plot.
    x (str): The column name in the dataframe to be plotted on the x-axis.
    color (str): The column name in the dataframe to be used for color coding the plot.

    Returns:
    px.ecdf: A Plotly ECDF plot object.
    """
    fig = px.ecdf(df.to_pandas(), x=x, color=color, marginal="histogram")
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig

@apply_fuzzy_matching()
def plot_parallel_coordinates(df: cudf.DataFrame) -> px.parallel_coordinates:
    """
    Generates a parallel coordinates plot using Plotly for the given cuDF DataFrame.

    Parameters:
    df (cudf.DataFrame): The input cuDF DataFrame containing the data to be plotted.

    Returns:
    px.parallel_coordinates: A Plotly parallel coordinates figure object.

    Notes:
    - The DataFrame is converted to a pandas DataFrame before plotting.
    - The plot uses 'total_bill' as the color dimension.
    - The color scale used is 'Tealrose' from Plotly's diverging color scales.
    - The color midpoint is set to 2.
    - The background of the plot and paper is set to be transparent.
    """
    fig = px.parallel_coordinates(df.to_pandas(), color="total_bill",
                                   color_continuous_scale=px.colors.diverging.Tealrose,
                                   color_continuous_midpoint=2)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })

    return fig

@apply_fuzzy_matching()
def plot_heatmap(df: cudf.DataFrame) -> px.parallel_coordinates:
    """
    Generates a heatmap plot from a cuDF DataFrame using Plotly.

    Parameters:
    df (cudf.DataFrame): The input DataFrame containing the data to be plotted.

    Returns:
    px.parallel_coordinates: A Plotly figure object representing the heatmap.

    Notes:
    - The DataFrame is converted to a pandas DataFrame before plotting.
    - The background color of the plot and paper is set to transparent.
    """
    fig = px.imshow(df.to_pandas())
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig

@apply_fuzzy_matching('x', 'y')    
def plot_pie(df: cudf.DataFrame, x: str, y: str) -> px.pie:
    """
    Generates a pie chart using Plotly Express from a cuDF DataFrame.

    Parameters:
    df (cudf.DataFrame): The cuDF DataFrame containing the data.
    x (str): The column name for the values of the pie chart.
    y (str): The column name for the names of the pie chart slices.

    Returns:
    px.pie: A Plotly Express pie chart figure object.
    """
    fig = px.pie(df.to_pandas(), values=x, names=y, color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig
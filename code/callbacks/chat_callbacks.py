import logging
import traceback
from dash import html, dcc, Input, Output, callback, State, no_update
from utils.configs import llm
from utils.utilities import get_dataframe, get_data_from_api
from utils.constants import DATETIME_FORMATS, NUMERIC_DTYPES, CATEGORICAL_DTYPES
from utils.cache_config import cache, cache_key
from textwrap import dedent
import plotly.express as px
import pandas as pd
import json
from chat.parse_code import process_response
from components.chat_tab import textbox
import plotly.io as pio
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def register_chat_callbacks(app):
    @app.callback(
        [Output("store-conversation", "data"),
         Output("loading-component", "children"),
         Output("submit", "disabled")],
        [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
        [State("user-input", "value"), State("store-conversation", "data")],
        prevent_initial_call=True
    )
    def run_chatbot(n_clicks, n_submit, user_input, chat_history):
        logger.debug(f"Callback triggered. n_clicks: {n_clicks}, n_submit: {n_submit}, user_input: {user_input}")
        
        try:
            if user_input is None or user_input.strip() == "":
                return no_update, no_update, no_update

         
            df = get_dataframe()
            schema = get_data_from_api("schema")
            sample_data = get_data_from_api("sample")
            columns = schema.get('columns', [])
            column_names = ', '.join(columns)
            
          
            categorical_columns = [col for col in columns if schema['dtypes'][col] in CATEGORICAL_DTYPES]
            numeric_columns = [col for col in columns if schema['dtypes'][col] in NUMERIC_DTYPES]
            datetime_columns = [col for col in columns if schema['dtypes'][col] in DATETIME_FORMATS]
                
            name = "AI Data Expert"

            # Add user input to chat history
            chat_history = json.loads(chat_history) if chat_history else []
            chat_history.append({"role": "user", "content": user_input})

            # Prepare context for the AI
            context = dedent(f"""
            You are an AI assistant named {name}. You have access to a dataframe with the following columns: 

            Categorical Columns {categorical_columns}
            Numeric Columns {numeric_columns}
            Datetime Columns {datetime_columns}

            The dataframe is already loaded and you may reference it as df. You do not need to instantiate it or create it.

            Here's a sample of the data:
            {sample_data}

            When asked about the data, you MUST perform analysis and create visualizations.
            ALWAYS include at least one code block and one figure in your response.

            IMPORTANT: Python code MUST be enclosed in <CODE> </CODE> tags.
            IMPORTANT: Figures MUST be enclosed in <FIGURE> </FIGURE> tags.
            IMPORTANT: Do not use backticks (`) for code blocks. Use <CODE> </CODE> tags.
            IMPORTANT: For visualizations, use Plotly Express (px). 
            
            CRITICAL: DO NOT PUT FIGURES INSIDE CODE BLOCKS. Figures may only be enclosed in <FIGURE> </FIGURE> tags.

            You should also return a response to the user's latest message in plain text.
            Do not use comments in code blocks.
            For any code, include a print statement so the output can be displayed.

            Example response format:

            Your data implies that there is a strong correlation between the columns.
            We can run python code to calculate the correlation.

            <CODE>
            correlation = df['column1'].corr(df['column2'])
            print(f"The correlation between column1 and column2 is: ")
            </CODE>

            We can visualize this using a scatter plot.
            
            <FIGURE>
            fig = px.scatter(df, x='age', y='income', title='Age vs Income')
            </FIGURE>
            
            <FIGURE>
            fig = px.histogram(df, x='age', nbins=20, title='Age Distribution')
            </FIGURE>
            
            For scatter plots with trend lines, use 'ols' (lowercase) as the trendline parameter:

            <FIGURE>
            fig = px.scatter(df, x='Season', y='Humidity', trendline='ols', title='Humidity vs Season')
            </FIGURE>

            Remember, ALWAYS include at least one <CODE> block and one <FIGURE> block in your response.
            Please provide a response to the user's latest message, including code and a figure.
            """)

            model_input = context + json.dumps(chat_history)

            response = llm.get_response(model_input)
        
            chat_history.append({
            "role": "assistant",
            "content": response
            })
            
            return json.dumps(chat_history), None, False

        except Exception as e:
            logger.error(traceback.format_exc())
            return no_update, html.Div(f"An error occurred: {str(e)}"), False



    @app.callback(
    Output("display-conversation", "children"),
    [Input("store-conversation", "data")]
    )
    def update_display(chat_history):
        if not chat_history:
            return []
        
        chat_history = json.loads(chat_history)
        
        messages = []
        for message in chat_history:
            if message["role"] == "user":
                messages.append(textbox(message["content"], box="user"))
            elif message["role"] == "assistant":
                response = process_response(message["content"])
                
                content = []
                for result in response["results"]:
                    if result["type"] == "text":
                        content.append(html.P(result["content"]))
                    elif result["type"] == "code":
                        content.append(html.Div([
                            html.H6("Code:", style={"margin-top": "10px", "margin-bottom": "5px"}),
                            html.Pre(result["content"], style={"background-color": "black", "color": "#90EE90", "padding": "10px", "border-radius": "5px"}),
                            html.H6("Output:", style={"margin-top": "10px", "margin-bottom": "5px"}),
                            html.Pre(result["output"], style={"background-color": "#e0e0e0", "padding": "10px", "border-radius": "5px"})
                        ]))
                    elif result["type"] == "figure":
                        content.append(html.Div([
                            dbc.Card([
                            dcc.Graph(
                                figure=result["content"],
                                config={'displayModeBar': False},
                            ),
                            ], className="chat-plot-card"),
                        ]))
                    elif result["type"] == "error":
                        if content:
                            content.pop()  
                        continue
                
                messages.append(textbox(html.Div(content, style={"margin-bottom": "20px"}), box="AI"))
        
        return messages
import logging
import traceback
from dash import html, dcc, Input, Output, State, no_update
from utils.configs import get_llm
from utils.utilities import get_dataframe, get_data_from_api
from utils.constants import DATETIME_FORMATS, NUMERIC_DTYPES, CATEGORICAL_DTYPES
from prompts.chat_prompt_template import context
import json
from chat.parse_code import process_response
from components.chat_tab import textbox
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import json


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
        """
        Handles the chatbot interaction by processing user input and generating a response.
        Args:
            n_clicks (int): Number of times the submit button has been clicked.
            n_submit (int): Number of times the user has submitted input.
            user_input (str): The input provided by the user.
            chat_history (str): JSON string representing the chat history.
        Returns:
            tuple: A tuple containing:
                - Updated chat history as a JSON string.
                - None if no error, otherwise an HTML Div with the error message.
                - Boolean indicating whether an error occurred (False if no error).
        """
        
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
                
            
           
            chat_history = json.loads(chat_history) if chat_history else []
            chat_history.append({"role": "user", "content": user_input})

            prompt = context.replace("{{user_input}}", user_input).replace("{{column_names}}", column_names).replace("{{categorical_columns}}", ', '.join(categorical_columns)).replace("{{numeric_columns}}", ', '.join(numeric_columns)).replace("{{datetime_columns}}", ', '.join(datetime_columns))
            print("PROMPT: ", prompt)
             
            model_input = prompt + json.dumps(chat_history)
            llm = get_llm()
            response = llm.get_response(model_input)
        
            chat_history.append({
            "role": "assistant",
            "content": response
            })
            
            return json.dumps(chat_history), None, False

        except Exception as e:
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
                        print("FIGURE FOUND")
                        try:
                            content.append(html.Div([
                                dbc.Card([
                                    dcc.Graph(
                                        figure=result["content"],
                                        config={'displayModeBar': False},
                                    ),
                                ], className="chat-plot-card"),
                            ]))
                            print("FIGURE: ", result["content"])
                        except Exception as e:
                            print(f"Error displaying figure: {str(e)}")
                            content.append(html.P(f"Error displaying figure: {str(e)}"))
                    elif result["type"] == "error":
                        print("ERROR: ", result["content"])
                        pass
                
                messages.append(textbox(html.Div(content, style={"margin-bottom": "20px"}), box="AI"))
        
        return messages
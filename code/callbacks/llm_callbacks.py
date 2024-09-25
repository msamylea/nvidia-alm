from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
from utils.llm_factory import get_llm
from utils.llm_singleton import llm_holder
import dash
from utils.constants import LLM_PROVIDERS

def register_llm_callbacks(app):
    @app.callback(
        Output("llm-setup-output", "children"),
        Output('llm-config-modal', 'is_open', allow_duplicate=True),
        Output('connection-success', 'is_open'),
        Input('main-tabs', 'value'),
        Input('llm-submit', 'n_clicks'),
        State('llm-config-modal', 'is_open'),
        State("llm-provider", "value"),
        State("llm-model", "value"),
        State("llm-api-key", "value"),
        State("llm-temperature", "value"),
        State("llm-max-tokens", "value"),
        prevent_initial_call=True
    )
    def update_llm_config(active_tab, llm_submit_clicks, modal_is_open,
                          provider, model, api_key, temperature, max_tokens):

        """
        Callback function to update the LLM (Language Learning Model) configuration based on user inputs.
        Parameters:
        active_tab (str): The currently active tab in the UI.
        llm_submit_clicks (int): The number of times the submit button for LLM configuration has been clicked.
        modal_is_open (bool): Boolean indicating if the modal is open.
        provider (str): The LLM provider selected by the user.
        model (str): The specific model selected by the user.
        api_key (str): The API key for accessing the LLM provider.
        temperature (str): The temperature setting for the LLM, controlling the randomness of the output.
        max_tokens (str): The maximum number of tokens for the LLM output.
        Returns:
        tuple: A tuple containing a status message and a boolean indicating if there was an error.
        """
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if triggered_id == 'llm-submit':
            try:
                llm = get_llm(provider, model, api_key=api_key, 
                              temperature=float(temperature) if temperature else None, 
                              max_tokens=int(max_tokens) if max_tokens else None)
                
                llm_holder.llm = llm
                
                provider_name = next(key for key, value in LLM_PROVIDERS.items() if value == provider)
                
                llm_setup_output = f"Provider: {provider_name}, Model: {model}"
                return llm_setup_output, False, True
            except ValueError as e:
                return f"Error: Invalid API key - {str(e)}", True, False
            except Exception as e:
                return f"Error setting up LLM: {str(e)}", True, False
        
        if llm_holder.llm is not None:
            provider_name = next(key for key, value in LLM_PROVIDERS.items() if value == llm_holder.llm.provider)
            return f"Provider: {provider_name}, Model: {llm_holder.llm.model}", False, False
        else:
            return "No LLM connected", False

    @app.callback(
        Output('llm-config-modal', 'is_open', allow_duplicate=True),
        Input('llm-config-button', 'n_clicks'),
        State('llm-config-modal', 'is_open'),
        prevent_initial_call=True
    )
    def toggle_modal(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
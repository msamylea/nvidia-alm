from dash import Input, Output, State, html, callback_context
from dash.exceptions import PreventUpdate
from utils.llm_factory import get_llm
from utils.llm_singleton import llm_holder
import dash
import dash_bootstrap_components as dbc
from utils.constants import LLM_PROVIDERS

def register_llm_callbacks(app):
    @app.callback(
        Output("error-toast", "is_open", allow_duplicate=True),
        Output("error-message", "children", allow_duplicate=True),
        Output("llm-setup-output", "children"),
        Output('llm-config-modal', 'is_open', allow_duplicate=True),
        Output('alert-placeholder', 'children', allow_duplicate=True),
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
        Update the configuration of the LLM (Language Learning Model) based on user inputs.
        Parameters:
        active_tab (str): The currently active tab in the UI.
        llm_submit_clicks (int): The number of times the submit button has been clicked.
        modal_is_open (bool): Whether the modal is open or not.
        provider (str): The provider of the LLM.
        model (str): The model of the LLM.
        api_key (str): The API key for accessing the LLM.
        temperature (float): The temperature setting for the LLM.
        max_tokens (int): The maximum number of tokens for the LLM.
        Returns:
        tuple: A tuple containing:
            - (bool): Whether to show an error alert.
            - (str or None): The error message if an error occurred, otherwise None.
            - (str or dash.no_update): The LLM setup output message or no update.
            - (bool): Whether to show the modal.
            - (dbc.Alert or bool): The alert component if successful, otherwise False.
        """
        ctx = callback_context
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
                alert = dbc.Alert("LLM Connection Established", color="#76b900", dismissable=True)
                return False, None, llm_setup_output, False, alert
            except ValueError as e:
                return True, f"Error: Invalid API key - {str(e)}", dash.no_update, True, False
            except Exception as e:
                return True, f"Error setting up LLM: {str(e)}", dash.no_update, True, False
        
        if llm_holder.llm is not None:
            provider_name = next(key for key, value in LLM_PROVIDERS.items() if value == llm_holder.llm.config.provider)
            return False, dash.no_update, f"Provider: {provider_name}, Model: {llm_holder.llm.config.model}", False, False
        else:
            return dash.no_update, dash.no_update, "No LLM connected", False, False
            

    @app.callback(
    Output("card-alert-placeholder", "children", allow_duplicate=True),
    Input("alert-placeholder", "children"),
    prevent_initial_call=True
    )
    def update_card_alert(alert_content):
        """
        Updates the card alert with the given content.

        Args:
            alert_content (str): The content to update the alert with.

        Returns:
            str: The updated alert content.
        """
        return alert_content

    @app.callback(
        Output('llm-config-modal', 'is_open', allow_duplicate=True),
        Input('llm-config-button', 'n_clicks'),
        State('llm-config-modal', 'is_open'),
        prevent_initial_call=True
    )
    def toggle_modal(n_clicks, is_open):
        """
        Toggles the state of a modal window.

        Args:
            n_clicks (int): The number of times the button has been clicked.
            is_open (bool): The current state of the modal window.

        Returns:
            bool: The new state of the modal window.
        """
        if n_clicks:
            return not is_open
        return is_open
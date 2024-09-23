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
                return llm_setup_output, False
            except ValueError as e:
                return f"Error: Invalid API key - {str(e)}", True
            except Exception as e:
                return f"Error setting up LLM: {str(e)}", True
        
        # For any other trigger (including tab changes and initial load)
        if llm_holder.llm is not None:
            provider_name = next(key for key, value in LLM_PROVIDERS.items() if value == llm_holder.llm.provider)
            return f"Provider: {provider_name}, Model: {llm_holder.llm.model}", False
        else:
            return "No LLM connected", False

    # Add a new callback to handle opening the modal
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
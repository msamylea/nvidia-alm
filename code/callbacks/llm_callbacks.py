from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from utils.llm_factory import get_llm
from utils.llm_singleton import llm_holder
import dash
from utils.constants import LLM_PROVIDERS

def register_llm_callbacks(app):
    @app.callback(
        Output("llm-setup-output", "children"),
        Output('llm-config-modal', 'is_open'),
        Output('connection-indicator', 'value'),
        Output('connection-indicator', 'color'),
        Input('llm-config-button', 'n_clicks'),
        Input('llm-submit', 'n_clicks'),
        State('llm-config-modal', 'is_open'),
        State("llm-provider", "value"),
        State("llm-model", "value"),
        State("llm-api-key", "value"),
        State("llm-temperature", "value"),
        State("llm-max-tokens", "value"),
    )
    def update_llm_config(config_button_clicks, llm_submit_clicks, modal_is_open,
                          provider, model, api_key, temperature, max_tokens):
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if triggered_id == 'llm-submit':
            try:
                llm = get_llm(provider, model, api_key=api_key, 
                              temperature=float(temperature) if temperature else None, 
                              max_tokens=int(max_tokens) if max_tokens else None)
                
                llm_holder.llm = llm
                
                provider_name = next(key for key, value in LLM_PROVIDERS.items() if value == provider)
                
                llm_setup_output = f"**Provider: {provider_name}, Model: {model}**"
                return llm_setup_output, not modal_is_open, True, 'green'
            except ValueError as e:
                llm_setup_output = f"Error: Invalid API key\n{str(e)}"
                return llm_setup_output, not modal_is_open, False, 'red'
            except Exception as e:
                llm_setup_output = f"Error setting up LLM:\n{str(e)}"
                return llm_setup_output, not modal_is_open, False, 'red'

        elif triggered_id == 'llm-config-button':
            return dash.no_update, not modal_is_open, dash.no_update, dash.no_update

        raise PreventUpdate
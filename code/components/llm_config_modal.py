import dash_bootstrap_components as dbc
from dash import dcc
from utils.constants import LLM_PROVIDER_OPTIONS

llm_config_modal = dbc.Modal([
    dbc.ModalHeader("LLM Configuration", style={'font-weight': 'bold', 'fontSize': '1.5rem', 'align-items': 'center'}),
    dbc.ModalBody([
        dbc.Select(
            id="llm-provider",
            options=LLM_PROVIDER_OPTIONS,
            placeholder="Select Provider"
        ),
        dbc.Input(id="llm-model", type="text", placeholder="Enter Model Name", className="mt-2"),
        dbc.Input(id="llm-api-key", type="password", placeholder="Enter API Key", className="mt-2"),
        dcc.Slider(
            min=0, max=1, step=0.1, value=0.5,
            id="llm-temperature",
            marks={i/10: str(i/10) for i in range(0, 11)},
            className="mt-3"
        ),
        dbc.Input(id="llm-max-tokens", type="number", placeholder="Enter Max Tokens", className="mt-2"),
        dbc.Button("Submit", id="llm-submit", color="primary", className="mt-3"),
    ]),
], className="custom-modal-body", id="llm-config-modal", is_open=False)
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_iconify import DashIconify

# Define a color scheme
COLORS = {
    "primary": "#364652",
    "secondary": "#EF8354",
    "background": "#F4F7F9",
    "text": "#333333"
}

# Common styles
card_style = {
    "height": "250px",
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "space-between",
    "padding": "25px",
    "backgroundColor": "white",
    "borderRadius": "10px",
    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "transition": "all 0.3s ease",
}

button_style = {
    "width": "100%",
    "marginTop": "20px",
    "backgroundColor": COLORS["primary"],
    "borderColor": COLORS["primary"],
}

home_content = html.Div([
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.H4("Step 1: Configure LLM", className="card-title mb-4"),
                        dbc.Button([
                            DashIconify(icon="carbon:machine-learning-model", width=24, className="me-2"),
                            "Configure LLM"
                        ], id="llm-config-button", color="primary", className="mt-auto", style=button_style),
                    ], style=card_style)
                ], width=6, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        html.H4("Step 2: Upload Dataset", className="card-title mb-4"),
                        dcc.Upload(
                            id='upload-data',
                            children=dbc.Button([
                                DashIconify(icon="carbon:data-base", width=24, className="me-2"),
                                "Upload Dataset"
                            ], color="primary", className="mt-auto", style=button_style),
                            multiple=False,
                        ),
                        dbc.Alert("File successfully uploaded", id="upload-success", color="success", dismissable=True, is_open=False, className="mt-3"),
                    ], style=card_style)
                ], width=6, className="mb-4"),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.H4("Step 3: Enter Query and Generate Report", className="card-title mb-4"),
                        dbc.Textarea(id="llm-prompt", placeholder="Enter your query or analysis target here...", 
                                     style={'width': '100%', 'height': '80px', 'resize': 'none'}),
                        dbc.Button([
                            DashIconify(icon="carbon:report", width=24, className="me-2"),
                            "Generate Report"
                        ], id="btn-open-pdf-modal", color="primary", className="mt-3", style=button_style),
                    ], style=card_style)
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        html.H4("Step 4: Create Presentation", className="card-title mb-4"),
                        dbc.Button([
                            DashIconify(icon="carbon:presentation-file", width=24, className="me-2"),
                            "Generate Presentation"
                        ], id="btn-open-presentation-modal", color="primary", className="mt-auto", style=button_style),
                        dcc.Download(id="download-pptx"),
                    ], style=card_style)
                ], width=6),
                dcc.Loading(
                id="loading-spinner",
                children=[html.Div(id="analysis-output")],
                type="graph",
                color=COLORS["secondary"],
                style={
                    "position": "fixed",
                    "top": 0,
                    "left": 0,
                    "right": 0,
                    "bottom": 0,
                    "backgroundColor": "rgba(0, 0, 0, 0.5)",
                    "zIndex": 9999,
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                },
                target_components={"analysis-output": "*"}
            ),
            ]),
        ], style={"backgroundColor": COLORS["background"], "padding": "30px"})
    ], className="main-home-card", style={"border": "none", "backgroundColor": COLORS["background"]}),
    
])
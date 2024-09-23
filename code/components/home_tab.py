import dash_bootstrap_components as dbc
from dash import dcc, html

# Define a common style for all cards
card_style = {
    "height": "200px",  
    "width": "600px",
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "space-between",
    "padding": "20px",
}

home_content = html.Div([
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dcc.Markdown("**Step 1: Configure LLM**", className="home-card-heading"),
                        dbc.Button(
                            "Configure LLM",
                            id="llm-config-button",
                            color="primary",
                            className="custom-btn mt-auto",
                            n_clicks=0,
                            style={'width': '50%'}
                        ),
                    ], className="home-card", style=card_style)
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dcc.Markdown("**Step 2: Upload Dataset**", className="home-card-heading"),
                        dcc.Upload(
                            id='upload-data',
                            children=dbc.Button(
                                "Upload Dataset",
                                color="primary",
                                className="custom-btn mt-auto",
                                style={'width': '50%'}
                            ),
                            multiple=False,
                        ),
                        dbc.Alert("File successfully uploaded", id="upload-success", color="success", dismissable=True, is_open=False, className="mt-2"),
                    ], className="home-card", style=card_style)
                ], width=6),
            ], className="mb-4"),  # Add margin between rows
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dcc.Markdown("**Step 3: Enter Query and Generate Report**", className="home-card-heading"),
                        dbc.Textarea(id="llm-prompt", placeholder="Enter your query or analysis target here...", 
                                     style={'width': '100%', 'height': '60px', 'backgroundColor': 'white', 'border': '1px solid #364652'}),
                        dbc.Button("Generate Report", id="btn-open-pdf-modal", color="primary", className="custom-btn mt-3", style={'width': '50%'}),
                    ], className="home-card", style=card_style)
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dcc.Markdown("**Step 4: Create Presentation**", className="home-card-heading"),
                        dbc.Button("Generate Presentation", id="btn-open-presentation-modal", color="primary", className="custom-btn mt-auto", style={'width': '50%'}),
                        dcc.Download(id="download-pptx"),
                    ], className="home-card", style=card_style)
                ], width=6),
            ]),
            dcc.Loading(
                id="loading-spinner",
                children=[html.Div(id="analysis-output", className="mt-4")],
                type="graph",
                color="#EF8354",
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
            )
        ])
    ], className="main-home-card")
])
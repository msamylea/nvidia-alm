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
    "boxShadow": "0 4px 6px #76b900",
    "transition": "all 0.3s ease",
    "marginTop": "40px",
    "marginRight": "20px",
    "borderTop": "5px solid #76b900",
}

button_style = {
    "width": "100%",
    "marginTop": "20px",
    "backgroundColor": COLORS["primary"],
    "borderColor": COLORS["primary"],
    "fontFamily": "Open Sans",
}

home_content = html.Div([
    dbc.Container([
               dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                DashIconify(icon="bi:1-circle", width=44),
                                html.H4("  Configure LLM", className="custom-card-title")  # Add the text beside the icon
                            ], className="d-flex align-items-center")  # Use flexbox to align items
                        ])
                    ]),
                    html.Div(id="card-alert-placeholder"),
                    dbc.Button([
                        DashIconify(icon="carbon:ai-launch", width=24, className="me-2"),
                        "Configure LLM"
                    ], id="llm-config-button", color="primary", className="mt-auto", style=button_style),
                ], class_name="home-inner-card", style=card_style)
            ], width=4, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                DashIconify(icon="bi:2-circle", width=44),
                                html.H4("  Upload Dataset", className="custom-card-title")  # Add the text beside the icon
                            ], className="d-flex align-items-center")  # Use flexbox to align items
                        ])
                    ]),
                    dbc.Alert("File successfully uploaded", id="upload-success", color="#76b900", dismissable=True, is_open=False, className="mt-3"),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            dbc.Button([
                                DashIconify(icon="carbon:data-table", width=24, className="me-2"),
                                "Upload Dataset"
                            ], color="primary", className="mt-auto", style=button_style)
                        ], className='mt-4', style={"width": "100%"})
                    ),
                    
                ], class_name="home-inner-card", style=card_style)
            ], width=4, className="mb-4"),
        ], justify="center"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                DashIconify(icon="bi:3-circle", width=44),
                                html.H4("  Enter Query and Generate Report", className="custom-card-title")  # Add the text beside the icon
                            ], className="d-flex align-items-center")  # Use flexbox to align items
                        ])
                    ]),
                    dbc.Textarea(id="llm-prompt", placeholder="Enter your query or analysis target here...", 
                                 style={'width': '100%', 'height': '80px', 'resize': 'none', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
                    dbc.Button([
                        DashIconify(icon="carbon:report", width=24, className="me-2"),
                        "Generate Report"
                    ], id="btn-open-pdf-modal", color="primary", className="mt-3", style=button_style),
                ], class_name="home-inner-card", style=card_style)
            ], width=4),
           dbc.Col([
                dbc.Card([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                DashIconify(icon="bi:4-circle", width=44),
                                html.H4("  Create Presentation", className="custom-card-title")  # Add the text beside the icon
                            ], className="d-flex align-items-center")  # Use flexbox to align items
                        ])
                    ]),
                    dbc.Button([
                        DashIconify(icon="mingcute:presentation-2-line", width=24, className="me-2"),
                        "Generate Presentation"
                    ], id="btn-open-presentation-modal", color="primary", className="mt-auto", style=button_style),
                ], class_name="home-inner-card", style=card_style)
            ], width=4),
        ], justify="center"),
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
        dcc.Loading(
            id="plot-spinner",
            children=[html.Div(dcc.Download(id="download-pptx"))],
            type="default",
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
            target_components={"download-pptx": "*"}
        ),
    ], className="main-home-card", fluid=True)
], style={"border": "none", "backgroundColor": "#53655c", "display": "flex", "justifyContent": "center", "alignItems": "center", "height": "100vh"})
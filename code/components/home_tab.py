import dash_bootstrap_components as dbc
from dash import dcc, html

home_content = html.Div([
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dcc.Markdown("**Step 1: Configure LLM**", className="home-card-heading"),
                        dbc.Button(
                            children=[
                                dbc.Row([
                                    dbc.Col("Configure LLM", width="auto"),
                                ])
                            ],
                            id="llm-config-button",
                            color="primary",
                            className="custom-btn",
                            n_clicks=0,
                            style={'width': '25%'}
                        ),
                    ], className="home-card")
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dcc.Markdown("**Step 2: Upload Dataset**", className="home-card-heading"),
                        dcc.Upload(id='upload-data',                     
                            children=dbc.Button(
                                children=[
                                    dbc.Row([
                                        dbc.Col("Upload Dataset", width="auto"),
                                    ])
                                ],
                                color="primary",
                                className="custom-btn"
                            ),
                            multiple=False,
                        )
                    ], className="home-card")
                ], width=6),
            ]),
            dbc.Card([
                dcc.Markdown("**Step 3: Enter Query and Generate Report**", className="home-card-heading"),
                html.Div([
                    html.H4("Analysis Target", className="info-box-heading"),
                    dbc.Textarea(id="llm-prompt", placeholder="Enter your query or analysis target here...", style={'width': '100%', 'height': 100, 'backgroundColor': 'white', 'border': '1px solid #364652'}),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(dbc.Button("Generate Report", id="btn-open-pdf-modal", color="primary", className="custom-btn", disabled=False), width="auto"),
                       
                    ]),
                    html.Div(id="analysis-output", className="mt-4")
                ])
            ], className="home-card"),
            dcc.Loading(
                id="loading-spinner",
                children=[
                    html.Div(id="analysis-output", className="mt-4")
                ],
                type="graph",
                color="#EF8354"
            )
        ])
    ], className="main-home-card")
])
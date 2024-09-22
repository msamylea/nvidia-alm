import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback_context, callback
from dash.exceptions import PreventUpdate


home_content = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Analysis Target", className="info-box-heading"),
                    html.P("Enter analysis target or query.", className='info-box-text'),
                    dbc.Textarea(id="llm-prompt", placeholder="Enter your query or analysis target here...", style={'width': '100%', 'height': 100, 'backgroundColor': 'white'}),
                    html.Br(),
                    dbc.Button("Generate Report", id="btn-open-pdf-modal", color="primary", className="custom-btn", disabled=False),
                    dbc.Button("Download PPTX", id="btn-download-pptx", color="primary", className="custom-btn"),
                    dcc.Download(id="download-pptx")
                ])
            ], className="info-box"),
            html.Br(),
            html.Br(),
            dcc.Loading(
                id="loading-spinner",
                children=[
                    html.Div(id="analysis-output", className="mt-4")
                ],
                type="graph",
                color="#EF8354"
            ),
            
            
        ], width=12),
    ])
])
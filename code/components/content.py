import dash_bootstrap_components as dbc
from dash import dcc, html

content = html.Div([
    dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H4("Analysis Target", className="info-box-heading"),
                html.P("Enter analysis target or query.", className='custom-p'),
                html.Br(),
                dbc.Textarea(id="llm-prompt", placeholder="Enter your query or analysis target here...", style={'width': '100%', 'height': 100, 'backgroundColor': 'white'}),
                html.Br(),
                dbc.Button("Get Analysis", id="llm-submit-prompt", color="primary", className="custom-btn", disabled=False),
            ]),
        ])
    ], className="info-box"),
    html.Br(),

    dcc.Loading(
        html.Div(id="analysis-output", className="mt-4"),
        target_components={"analysis-output": "children"}
    )
], id="page-content")
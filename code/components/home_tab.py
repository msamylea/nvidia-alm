import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_ag_grid as dag

home_content = html.Div([
    html.Hr(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Analysis Target", className="info-box-heading"),
                    html.P("Enter analysis target or query.", className='info-box-text'),
                    dbc.Textarea(id="llm-prompt", placeholder="Enter your query or analysis target here...", style={'width': '100%', 'height': 100, 'backgroundColor': 'white'}),
                    html.Br(),
                    dbc.Button("Get Analysis", id="llm-submit-prompt", color="primary", className="custom-btn", disabled=False),
                ])
            ], className="info-box"),
            html.Br(),  # Add a break to create space between the card and the loading component
            dcc.Loading(
                html.Div(id="analysis-output", className="mt-4"),
                target_components={"analysis-output": "children"},
                type="graph",
                color="#EF8354"
            ),
        ], width=12),  # Adjust the width as needed
    ])
], id="page-content")
from dash import html
import dash_bootstrap_components as dbc
from utils.constants import LOGO_ICON

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=LOGO_ICON, height="60px"), width="auto", style={'marginRight': '20px', 'marginTop': '5px'}),
                                dbc.Col(dbc.NavbarBrand("AI Data Analysis", className="custom-navbar-brand")),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        width="auto",
                    ),
                ],
                align="center",
                className="g-0",
                style={"width": "auto"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                   dbc.Row(
                                        html.Div(
                                            "No data uploaded", 
                                            id='output-data-upload', 
                                            className="custom-navbar-text ml-auto", 
                                        )
                                    ),
                                    dbc.Row(
                                        html.Div(
                                            "No LLM connected", 
                                            id='llm-setup-output', 
                                            className="custom-navbar-text ml-auto",
                                        )
                                    ),
                                ], className="custom-navbar-card"
                            ),
                        ],
                        width="auto",
                        className="ml-auto",
                    ),
                ],
                align="center",
                className="g-0",
                style={"width": "auto"},
            ),
        ],
        style={'backgroundColor': '#364652', 'height': '100px', 'border-radius': '15px'},
        fluid=True,
    ),
    
)
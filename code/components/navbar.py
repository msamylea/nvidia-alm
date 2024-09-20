import dash_bootstrap_components as dbc
from dash import html
from utils.constants import LOGO_ICON

import dash_bootstrap_components as dbc


navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=LOGO_ICON, height="80px"), width="auto", style={'marginRight': '20px', 'marginTop': '5px'}),
                                dbc.Col(dbc.NavbarBrand("AI Data Analysis", className="custom-navbar-brand")),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        html.Div(id='output-data-upload', className="custom-navbar-text ml-auto"),
                        width="auto",
                        style={"marginLeft": "auto"},
                    ),
                ],
                align="center",  # Center align items vertically
                className="g-0",
                style={"width": "100%"},
            ),
        ],
        fluid=True,  # Make the container fluid to take full width
    ),
    color="#364652",
    dark=True,
    style={'borderRadius': '15px', 'boxShadow': '9px 10px 5px -6px rgba(0,0,0,0.32)', 'padding': '5px'}
)
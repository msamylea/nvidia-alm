import dash_bootstrap_components as dbc
from dash import html
from utils.constants import LOGO_ICON

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Img(src=LOGO_ICON, height="40px"), width="auto", style={'marginRight': '20px', 'marginTop': '5px'}),
                    dbc.Col(dbc.NavbarBrand("AI Data Analysis", className="custom-navbar-brand")),
                    dbc.Col(html.Div(id='output-data-upload', className="custom-navbar-text")),  # Moved this inside the main list
                ],
                align="left",
                className="g-0",
                style={"textDecoration": "none"},
            ),
        ], 
    ),
    color="#5E5C6C",
    dark=True,
    style={'borderRadius': '15px', 'boxShadow': '9px 10px 5px -6px rgba(0,0,0,0.32)', 'padding': '5px'}
)
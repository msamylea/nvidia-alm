import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_mantine_components as dmc
from utils.constants import PPT_THEME_OPTIONS

presentation_modal = dbc.Modal([
    dbc.ModalHeader("Presentation Style", style={'font-weight': 'bold', 'font-size': '1.5rem', 'align-items': 'center'}),
    dcc.Markdown("**Select a theme for your presentation. The theme will be applied to the entire presentation.**", style={'font-size': '1rem'}),
    dbc.ModalBody([
        dbc.Card([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Select Theme", className="ppt-inner-card-header"),
                        dbc.Select(
                            id="ppt-theme-choices",
                            options=PPT_THEME_OPTIONS,
                            placeholder="Select Theme",
                            style={'background-color': 'white'}
                        ),
                    ], className="ppt-theme-card-inner", style={'width': '100%', 'padding': '20px'}),
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Presentation Theme Previews", className="ppt-inner-card-header"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("BlackWhite", className="ppt-theme-header"),
                                    dmc.Image(radius='sm', src='assets/BlackWhite.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("BlueYellow", className="ppt-theme-header"),
                                    dmc.Image(radius='sm', src='assets/BlueYellow.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("Orange", className="ppt-theme-header"),
                                    dmc.Image(radius='sm', src='assets/Orange.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("Teal", className="ppt-theme-header"),
                                    dmc.Image(radius='sm', src='assets/Teal.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("BlueGrey", className="ppt-theme-header"),
                                    dmc.Image(radius='sm', src='assets/BlueGrey.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("RedGrey", className="ppt-theme-header"),
                                    dmc.Image(radius='sm', src='assets/RedGrey.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                               ], className="ppt-theme-card"),
                                ]),
                            ]),
                        ]),
                    ], className="mt-3", style={'width': '100%', 'padding': '20px'}),
                ]),
            ]),
        ], className="ppt-theme-maincard"),
        dbc.Button("Submit", id="download_pptx", color="primary", className="mt-3"),
    ]),
], className="presentation-modal-body", id="presentation-modal", is_open=False, size="xl")
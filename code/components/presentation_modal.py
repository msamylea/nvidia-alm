import dash_bootstrap_components as dbc
from dash import html, dcc
from utils.constants import PPT_THEME_OPTIONS

presentation_modal = dbc.Modal([
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
                            style={'backgroundColor': 'white'}
                        ),
                    ], className="ppt-theme-card-inner", style={'width': '100%', 'padding': '20px'}),
                ]),
                dbc.Row([
                    dbc.Card([
                        dbc.CardHeader("Presentation Theme Previews", className="ppt-inner-card-header"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("BlackWhite", className="ppt-theme-header"),
                                    html.Img(src='assets/BlackWhite.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("BlueYellow", className="ppt-theme-header"),
                                    html.Img(src='assets/BlueYellow.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("Orange", className="ppt-theme-header"),
                                    html.Img(src='assets/Orange.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("Teal", className="ppt-theme-header"),
                                    html.Img(src='assets/Teal.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("BlueGrey", className="ppt-theme-header"),
                                    html.Img(src='assets/BlueGrey.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                                ], className="ppt-theme-card"),
                                ]),
                                dbc.Col([
                                    dbc.Card([
                                    dbc.CardHeader("RedGrey", className="ppt-theme-header"),
                                    html.Img(src='assets/RedGrey.png', className="mt-2", style={'width': '200px', 'height': '100px'}),
                               ], className="ppt-theme-card"),
                                ]),
                            ]),
                        ]),
                    ], className="mt-3", style={'width': '100%', 'padding': '20px'}),
                ]),
            ]),
        ], className="ppt-theme-maincard"),
        html.Div(
            dbc.Button("Submit", id="download_pptx", color="primary", className="ml-auto"),
            className="d-flex justify-content-end"
        ),
    ]),
], className="presentation-modal-body", id="presentation-modal", is_open=False, size="xl")
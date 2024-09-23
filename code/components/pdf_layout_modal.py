import dash_bootstrap_components as dbc
from dash import dcc, html

pdf_modal = dbc.Modal([
    dbc.ModalHeader("Report Style Options", style={'font-weight': 'bold', 'fontSize': '1.5rem', 'align-items': 'center'}),
    dbc.ModalBody([
        dbc.Card([
            dbc.CardHeader("Optional: Add Logo and select color scheme for your report output.", className="pdf-theme-header"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Upload Logo", className="ppt-inner-card-header"),
                        dbc.Alert("Image should be approximately 300px x 120px", color="info", is_open=True, style={'fontSize': '0.8rem'}),
                        dcc.Upload(html.Button("Upload Logo", className="btn btn-primary"),
                            id="uploaded-logo",   
                            multiple=False,                        
                            style={'backgroundColor': 'white'}
                        ),
                    ], className="pdf-logo-card-inner", style={'width': '100%', 'padding': '20px'}),
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Select Colors", className="pdf-color-header"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader("Primary Color", className="inner-color-header"),
                                        dbc.Input(type="color", id="primary-color-picker", value="#1a73e8", style={'width': '100px', 'height': '50px'}),
                                    ], className="pdf-theme-card"),
                                ]),
                                ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader("Accent Color", className="inner-color-header"),
                                        dbc.Input(type="color", id="accent-color-picker", value="#fbbc04", style={'width': '100px', 'height': '50px'}),
                                    ], className="pdf-theme-card"),
                                ]),
                            ]),
                        ]),
                    ], className="mt-3", style={'width': '100%', 'padding': '20px'}),
                ]),
            ]),
        ], className="pdf-theme-maincard"),
        dbc.Button("Submit", id="llm-submit-prompt", color="primary", className="mt-3"),
        dcc.Download(id="download-pdf"),
    ]),
], className="pdf-modal-body", id="pdf-modal", is_open=False, size="xl")
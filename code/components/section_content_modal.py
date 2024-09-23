# import dash_bootstrap_components as dbc
# from dash import html, dcc

# def create_section_modal_body(outline_data):
#     section_modal = html.Div([
#         dbc.Card([
#             dbc.CardHeader(html.H4("Suggested Report Title and Sections"), className = "section-modal-card-header"),
#                 dbc.CardBody([
#                     html.Hr(),
#                     dcc.Markdown("_Change the report title if desired, and select sections to include in the final report._"),
#                     dbc.Card([
#                         dbc.CardBody([
#                             html.H5("Report Title:"),
                      
#                         dbc.Input(id={"type": "section-input", "index": 0}, value=outline_data['report_title'], type="text", className="mb-3"),
#                           ]),
#                     ], className = "section-modal-card-inner"),
#                     html.Hr(),
#                     dbc.Card([
#                         dbc.CardBody([
#                     html.H5("Select sections to include:"),
#                     html.Hr(),
#                     *[
#                         dbc.Checkbox(
#                             id={"type": "section-checkbox", "index": i},
#                             label=section["name"],
#                             value=section["selected"],
#                             className="mb-2"
#                         )
#                         for i, section in enumerate(outline_data["sections"])
#                     ],
#                         ]),
#                     ], className = "section-modal-card-inner"),
#                     html.Hr(),
#                     dbc.Card([
#                         dbc.CardBody([
#                         html.H5("Add a new section:"),
#                         dbc.Input(id={"type": "section-input", "index": -1}, placeholder="Enter a new section name", type="text", className="mt-3"),
#                         ]),
#                     ], className = "section-modal-card-inner"),
            
#                     html.Br(),
                    
#                 ], className="section-modal-card-body"),
#             ], className="section-modal-card"),

#         ])
        
#     return section_modal

import dash_bootstrap_components as dbc
from dash import html, dcc

def create_section_modal_body(outline_data):
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Suggested Report Title and Sections"), className="section-modal-card-header"),
                    dbc.CardBody([
                        html.Hr(),
                        dcc.Markdown("_Change the report title if desired, and select sections to include in the final report._"),
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Report Title:"),
                                dbc.Input(id={"type": "section-input", "index": 0}, value=outline_data['report_title'], type="text", className="mb-3"),
                            ]),
                        ], className="section-modal-card-inner"),
                        html.Hr(),
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Select sections to include:"),
                                html.Hr(),
                                *[
                                    dbc.Checkbox(
                                        id={"type": "section-checkbox", "index": i},
                                        label=section["name"],
                                        value=section["selected"],
                                        className="mb-2"
                                    )
                                    for i, section in enumerate(outline_data["sections"])
                                ],
                            ]),
                        ], className="section-modal-card-inner"),
                        html.Hr(),
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Add a new section:"),
                                dbc.Input(id={"type": "section-input", "index": -1}, placeholder="Enter a new section name", type="text", className="mt-3"),
                            ]),
                        ], className="section-modal-card-inner"),
                    ], className="section-modal-card-body"),
                ], className="section-modal-card"),
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Optional: Add Logo and select color scheme for your report output.", className="pdf-theme-header"),
                    dbc.CardBody([
                        dbc.Card([
                            dbc.CardHeader("Upload Logo", className="ppt-inner-card-header"),
                            dbc.CardBody([
                                dbc.Alert("Image should be approximately 300px x 120px", color="info", is_open=True, style={'fontSize': '0.8rem'}),
                                dcc.Upload(
                                    html.Button("Upload Logo", className="btn btn-primary"),
                                    id="uploaded-logo",   
                                    multiple=False,                        
                                    style={'backgroundColor': 'white'}
                                ),
                            ]),
                        ], className="pdf-logo-card-inner", style={'width': '100%', 'padding': '20px'}),
                        html.Br(),
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
                ], className="pdf-theme-maincard"),
            ], width=6),
            dcc.Download(id="download-pdf"),
        ]),
    ])
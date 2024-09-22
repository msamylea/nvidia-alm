import dash_bootstrap_components as dbc
from dash import html, dcc

def create_section_modal_body(outline_data):
    section_modal = html.Div([
        dbc.Card([
            dbc.CardHeader(html.H4("Suggested Report Title and Sections"), className = "section-modal-card-header"),
                dbc.CardBody([
                    html.Hr(),
                    dcc.Markdown("_Change the report title if desired, and select sections to include in the final report._"),
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Report Title:"),
                      
                        dbc.Input(id={"type": "section-input", "index": 0}, value=outline_data['report_title'], type="text", className="mb-3"),
                          ]),
                    ], className = "section-modal-card-inner"),
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
                    ], className = "section-modal-card-inner"),
                    html.Hr(),
                    dbc.Card([
                        dbc.CardBody([
                        html.H5("Add a new section:"),
                        dbc.Input(id={"type": "section-input", "index": -1}, placeholder="Enter a new section name", type="text", className="mt-3"),
                        ]),
                    ], className = "section-modal-card-inner"),
            
                    html.Br(),
                    
                ], className="section-modal-card-body"),
            ], className="section-modal-card"),

        ])
        
    return section_modal
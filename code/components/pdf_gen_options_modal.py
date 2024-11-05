import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback

def create_section_modal_body(outline_data):
    """
    Creates the body of a modal for configuring PDF generation options.
    Parameters:
    outline_data (dict): A dictionary containing the report title and sections information.
        - report_title (str): The suggested title for the report.
        - sections (list of dict): A list of sections where each section is a dictionary with:
            - name (str): The name of the section.
            - selected (bool): Whether the section is selected to be included in the report.
    Returns:
    html.Div: A Dash HTML component containing the layout for the modal body, which includes:
        - A section for changing the report title and selecting sections to include.
        - An optional section for adding a new section.
        - An optional section for report styling, including company name, logo upload, and color scheme selection.
    """
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Suggested Report Title and Sections"), className="section-modal-card-header"),
                    dbc.CardBody([
                        dcc.Markdown("_Change the report title if desired, and select sections to include in the final report._"),
                        html.Hr(),
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Report Title:", className="mb-2"),
                                dbc.Input(id={"type": "section-input", "index": 0}, value=outline_data['report_title'], type="text", className="mb-3", style={"backgroundColor": "#f9f9f9"}),
                            ]),
                        ], className="section-modal-card-inner mb-3"),
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Select sections to include:", className="mb-2"),
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
                        ], className="section-modal-card-inner mb-3"),
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Optional: Add new section:", className="mb-2"),
                                dbc.Input(id={"type": "section-input", "index": -1}, placeholder="Enter a new section name", type="text", style={"backgroundColor": "#f9f9f9"}),
                            ]),
                        ], className="section-modal-card-inner"),
                    ], className="section-modal-card-body"),
                ], className="section-modal-card h-100"),
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Optional: Report Styling"), className="section-modal-card-header"),
                    dbc.CardBody([
                        dcc.Markdown("_Add Logo and select color scheme for your report output._"),
                        html.Hr(),
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Company Name:", className="mb-2"),
                                dbc.Input(
                                    type = "text",
                                    id="company-name",                            
                               
                                ),
                            ]),
                        ], className="section-modal-card-inner mb-3"),
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Upload Logo:", className="mb-2"),
                                dbc.Alert("Image should be approximately 300px x 120px", color="info", className="mb-2"),
                                dcc.Upload(
                                    id="uploaded-logo",
                                    children=dbc.Button("Upload Logo", color="primary", className="w-100"),
                                    multiple=False,
                                ),
                                html.Div(id="logo-preview", className="mt-2"),
                            ]),
                        ], className="section-modal-card-inner mb-3"),
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Select Colors:", className="mb-2"),
                                dcc.Markdown("_Primary used for page elements and numbering. Accent used for table headers._", className="mb-3"),
                                html.Div([
                                    html.Label("Primary Color:", className="mb-2"),
                                    dbc.Input(type="color", id="primary-color-picker", value="#76B900", style={'width': '100%', 'height': '40px'}),
                                ], className="mb-3"),
                                html.Div([
                                    html.Label("Accent Color:", className="mb-2"),
                                    dbc.Input(type="color", id="accent-color-picker", value="#aad361", style={'width': '100%', 'height': '40px'}),
                                ]),
                            ]),
                        ], className="section-modal-card-inner"),
                    ], className="section-modal-card-body"),
                ], className="section-modal-card h-100"),
            ], width=6),
        ]),
    ])
    
@callback(
    Output("logo-preview", "children"),
    Input("uploaded-logo", "contents"),
)
def update_logo_preview(contents):
    """
    Updates the logo preview with the provided image contents.

    Args:
        contents (str): The base64-encoded contents of the image to be displayed.

    Returns:
        html.Img: An HTML image element with the provided contents as the source and a maximum width of 25%.
    """
    if contents is not None:
        return html.Img(src=contents, style={"max-width": "25%"})
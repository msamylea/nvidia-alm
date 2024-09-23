# import dash_bootstrap_components as dbc
# from dash import dcc, html
# import dash_daq as daq

# sidebar = dbc.Nav(
#     children=[
#         dbc.Card([
#             html.Br(),
#             html.Br(),
#             dbc.NavItem(
#                 children=[
#                     dbc.Button(
#                         children=[
#                             dbc.Row([
#                                 dbc.Col("Configure LLM   ", width="auto", className="d-flex align-items-center"),
#                                 dbc.Col(daq.Indicator(id='connection-indicator', value=False, color='#CC2936', size=20, theme='dark'), width="auto"),
#                             ], className="no-gutters flex-nowrap align-items-center justify-content-between"),
#                         ],
#                         id="llm-config-button",
#                         color="primary",
#                         className="custom-btn",
#                     ),
#                 ],
#                 style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
#             ),
#             html.Br(),
#             dbc.NavItem(
#                 children=[
#                     dcc.Upload(
#                         dbc.Button(
#                             children=[
#                                 dbc.Row([
#                                     dbc.Col("Upload Dataset", width="auto", className="d-flex align-items-center"),
#                                     dbc.Col(daq.Indicator(id='file-indicator', value=False, color='#CC2936', size=20, theme='dark'), width="auto", className="ml-3"),
#                                 ], className="no-gutters flex-nowrap align-items-center justify-content-between"),
#                             ],
#                             id="upload-data-button",
#                             color="primary",
#                             className="custom-btn",
#                         ),
#                         id='upload-data',
#                         multiple=False,
#                         style={'height': '100%'}
#                     ),
#                 ],
#                 style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
#             ),
#             html.Br(),
            
#             html.Div(id='llm-setup-output', className="mt-3"),
#             html.Br(),
#         ],  className="side-card", style={'height': '100%', 'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-start', 'align-items': 'center'}),
#     ],
#     vertical=True,
#     style={'height': '100%', 'paddingTop': '30px', 'paddingLeft': '40px'},
#     horizontal="start"
# )
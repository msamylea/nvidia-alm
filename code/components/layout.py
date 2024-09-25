import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
from components.navbar import navbar
from components.llm_config_modal import llm_config_modal
from .home_tab import home_content
from .chat_tab import chat_content
from .presentation_modal import presentation_modal


tabs = dcc.Tabs(
    id="main-tabs",
    className='custom-tabs',
    value='home',
    children=[
        dcc.Tab(label='Home', value='home', className='custom-tab', selected_className='selected-custom-tab'),
        dcc.Tab(label='Chat', value='chat', className='custom-tab', selected_className='selected-custom-tab'),
    ],

)

error_toast = dbc.Toast(
    html.P(id="error-message"),
    id="error-toast",
    is_open=False,
    header="Information Alert",
    icon="info",
    dismissable=True,
    style={
        "position": "fixed",
        "top": "50%",
        "left": "50%",
        "transform": "translate(-50%, -50%)",
        "zIndex": 9999,
        "height": "auto",
        "width": "auto",
        "border": "10px solid #76b900",
        "borderRadius": "15px",
},
    body_style = {
        "fontSize": "1rem",
        "fontWeight": "bold",
        "backgroundColor": "white",
        "color": "black",
        "padding": "40px",
    },
    header_style = {
        "fontSize": "1rem",
        "fontWeight": "bold",
        "borderBottom": "5px solid #76b900 ",
    }
)


def create_layout():
    return dbc.Container([
            dcc.Store(id="store-conversation", storage_type="memory"),
            dcc.Store(id='stored-data'),
            dcc.Store(id='pdf-buffer'), 
            dcc.Store(id='report-generated'),
            dcc.Store(id='report-generation-trigger', data=False),
            dcc.Store(id='report-data'),
            dcc.Store(id='open-pdf-modal', data=False),
            dcc.Store(id='outline-data'),
            dcc.Store(id='report-style-data'),
            html.Div(id='connection-status', style={'display': 'none'}),
            navbar,
            html.Div(id="alert-placeholder", hidden=True),
            llm_config_modal,
            presentation_modal,
            error_toast,
            dbc.Modal(
                [
                    dbc.ModalBody([
                        html.Div(id="section-modal-content")  # This will be replaced with the dynamic content
                    ]),
                    dbc.ModalFooter([
                        dbc.Button("Generate Report", id="submit-sections", className="ml-auto"),
                        dbc.Button("Cancel", id="cancel-sections", className="ml-2")
                    ])
                ],
                id="section-modal",
                size="xl",
                is_open=False,
            ),
            dbc.Row([
                dbc.Col(
                    [                   
                        tabs,
                        html.Div(id="tab-content"),
                        html.Br(),
                        ],
                    width=12
                )
            ], style={"height": "100vh"})
        ], fluid=True, className="dbc")


@callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'value')
)
def render_content(tab):
    if tab == 'home':
        return home_content
    elif tab == 'chat':
        return chat_content
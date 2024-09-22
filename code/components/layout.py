import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc
from components.navbar import navbar
from components.sidebar import sidebar
from components.content import content
from components.llm_config_modal import llm_config_modal
from components.pdf_layout_modal import pdf_modal
from .home_tab import home_content
from .chat_tab import chat_content
from .presentation_modal import presentation_modal

tabs = dbc.Tabs(
    [
        dbc.Tab(
            label="Reports",
            tab_id="home",
            tabClassName = "inner-tab-report",
            labelClassName="inner-tab-label"
        ),
        dbc.Tab(
            label="Chat",
            tab_id="chat",
            tabClassName="inner-tab-chat",
            labelClassName="inner-tab-label"
        ),
    ],
    id="tabs",
    active_tab="home",
    class_name="custom-tabs"
)

def create_layout():
    return dmc.MantineProvider(
        dbc.Container([
            dcc.Store(id="store-conversation", storage_type="memory"),
            dcc.Store(id='stored-data'),
            dcc.Store(id='pdf-buffer'), 
            dcc.Store(id='report-generated'),  #
            dcc.Store(id='report-data'),
            dcc.Store(id='open-pdf-modal', data=False),
            dcc.Store(id='outline-data'),
            html.Div(id='connection-status', style={'display': 'none'}),
            navbar,
            llm_config_modal,
            presentation_modal,
            pdf_modal,
            dbc.Modal(
                [
                    dbc.ModalBody(id="section-modal-body"),
                    dbc.ModalFooter([
                        dbc.Button("Submit", id="submit-sections", className="ml-auto"),
                        dbc.Button("Cancel", id="cancel-sections", className="ml-2")
                    ])
                ],
                id="section-modal",
                size="lg",
                is_open=False,
            ),
            dbc.Row([
                dbc.Col(sidebar, width=2),
                dbc.Col(
                    [                   
                        html.Br(),
                        html.Br(),
                        tabs,
                        html.Div(id="tab-content"),
                        html.Br(),
                        html.Br(),
                    ],
                    width=10
                )
            ], style={"height": "100vh"})
        ], fluid=True, className="dbc")
    )

@callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "home":
        return home_content
    elif active_tab == "chat":
        return chat_content
    else:
        return content

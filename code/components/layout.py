import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc
from components.navbar import navbar
from components.sidebar import sidebar
from components.content import content
from components.llm_config_modal import llm_config_modal
from .home_tab import home_content
from .predictions_tab import prediction_content
from .presentation_modal import presentation_modal

tabs = dbc.Tabs(
    [
        dbc.Tab(
            label="Home",
            tab_id="home",
            tabClassName = "inner-tab",
            labelClassName="inner-tab-label"
        ),
        dbc.Tab(
            label="Predictions",
            tab_id="predictions",
            tabClassName="inner-tab",
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
            dcc.Store(id='stored-data'),
            dcc.Store(id='report-data'),
            html.Div(id='connection-status', style={'display': 'none'}),
            navbar,
            llm_config_modal,
            presentation_modal,
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
    elif active_tab == "predictions":
        return prediction_content
    else:
        return content
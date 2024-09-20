from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

def textbox(content, box="AI", name="AI Data Expert"):
    style = {
        "max-width": "70%",
        "width": "max-content",
        "padding": "10px 15px",
        "border-radius": 18,
        "margin-bottom": 10,
        "white-space": "pre-wrap",
        "word-wrap": "break-word",
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0
        style["background-color"] = "#364652"
        style["color"] = "white"
    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"
        style["background-color"] = "#CDD5D1"
        style["color"] = "black"
    else:
        raise ValueError("Incorrect option for `box`.")

    if isinstance(content, dict):
        if content["type"] == "graph":
            return html.Div([
                html.Div(content["text"], style=style),
                dcc.Graph(figure=content["figure"], config={'displayModeBar': False}, style={"margin-top": "10px"})
            ], style={"margin-bottom": "20px"})
        else:
            return html.Div(content["text"], style=style)
    else:
        return html.Div(content, style=style)

chat_content = html.Div([
    dcc.Store(id="store-conversation", storage_type="memory"),
    dbc.Card([
    html.Div(id="display-conversation", style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(90vh - 200px)",
        "flex-direction": "column",
        "padding": "20px",
    }),
    dbc.Spinner(html.Div(id="loading-component"), color="primary"),
    html.Div([
        dbc.InputGroup([
            dbc.Input(id="user-input", placeholder="Type your message here...", type="text", size="lg"),
            dbc.Button("Send", id="submit", color="primary"),
        ], size="lg"),
    ], style={"padding": "20px", "background-color": "#f8f9fa"}),
], style={"height": "90vh", "display": "flex", "flex-direction": "column"})
], className="chat-card")
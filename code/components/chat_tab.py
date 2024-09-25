from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def textbox(content, box="AI", name="AI Data Expert"):
    style = {
        "maxWidth": "70%",
        "width": "max-content",
        "padding": "1px 1px",
        "borderRadius": 18,
        "marginBottom": 10,
        "alignSelf": "flexStart",
        "whiteSpace": "pre-wrap",
        "wordWrap": "break-word",
    }

    if box == "user":
        icon = DashIconify(icon="hugeicons:user-question-01", width=44, className="me-2")
        style["marginLeft"] = "auto"
        style["marginRight"] = 0
        style["backgroundColor"] = "#364652"
        style["padding"] = "10px 15px"
        style["color"] = "white"
    elif box == "AI":
        icon = DashIconify(icon="hugeicons:ai-chat-02", width=44, className="me-2")
        style["marginLeft"] = 0
        style["marginRight"] = "auto"
        style["backgroundColor"] = "#fff"
        style["padding"] = "10px 15px"
        style["color"] = "black"
        style["border"] = "6px solid #76b900"
    else:
        raise ValueError("Incorrect option for `box`.")

    if isinstance(content, dict):
        if content["type"] == "graph":
            return html.Div([
                html.Div([icon, content["text"]], style=style),
                dcc.Graph(figure=content["figure"], config={'displayModeBar': False}, style={"marginTop": "10px"})
            ], style={"marginBottom": "20px"})
        else:
            return html.Div([icon, content["text"]], style=style)
    else:
        return html.Div([icon, content], style=style)

chat_content = html.Div([
    dcc.Store(id="store-conversation", storage_type="memory"),
    dbc.Card([
        html.Div(id="display-conversation", style={
            "overflowY": "auto",
            "display": "flex",
            "height": "calc(70vh - 200px)",  # Adjust this value as needed
            "flexDirection": "column",
            "padding": "20px",
        }),
        dbc.Spinner(html.Div(id="loading-component"), color="primary"),
        html.Div([
            dbc.InputGroup([
                dbc.Input(id="user-input", placeholder="Type your message here...", type="text", size="lg", style={"borderRadius": "15px 0 0 15px"}),
                dbc.Button("Send", id="submit", color="primary", style={"borderRadius": "0 15px 15px 0"}),
            ], size="lg"),
        ], style={"borderRadius": 15, "backgroundColor": "#f8f9fa", "width": "100%", "margin-top": "auto"}),  
    ], className="chat-card", style={
        "display": "flex", 
        "flexDirection": "column",
        "width": "100%",
        "height": "70vh",
        "margin": "0",
    })
], style={
    "width": "90%",
    "maxWidth": "1600px",  
    "margin": "0 auto",
    "marginTop": "20px",
    "border": "none",
    "display": "flex",
    "justifyContent": "center",
})
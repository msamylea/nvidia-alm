from dash import html, dcc
import dash_bootstrap_components as dbc

def textbox(content, box="AI", name="AI Data Expert"):
    style = {
        "max-width": "70%",
        "width": "max-content",
        "padding": "1px 1px",
        "border-radius": 18,
        "margin-bottom": 10,
        "align-self": "flex-start",
        "white-space": "pre-wrap",
        "word-wrap": "break-word",
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0
        style["background-color"] = "#364652"
        style["padding"] = "10px 15px"
        style["color"] = "white"
    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"
        style["background-color"] = "#B1BEB8"
        style["padding"] = "10px 15px"
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
                "height": "calc(70vh - 200px)",  # Adjust this value as needed
                "flex-direction": "column",
                "padding": "20px",
            }),
            dbc.Spinner(html.Div(id="loading-component"), color="primary"),
            html.Div([
            dbc.InputGroup([
                dbc.Input(id="user-input", placeholder="Type your message here...", type="text", size="lg", style={"border-radius": "15px 0 0 15px"}),
                dbc.Button("Send", id="submit", color="primary", style={"border-radius": "0 15px 15px 0"}),
            ], size="lg"),
        ], style={"border-radius": 15, "background-color": "#f8f9fa", "width": "100%", "margin-top": "auto"}),  
        ], className="chat-card", style={
            "display": "flex", 
            "flex-direction": "column",
            "width": "100%",
            "height": "70vh",
            "margin": "0",
        })
    ], style={
        "width": "90%",
        "maxWidth": "1200px",  
        "margin": "0 auto",
        "margin-top": "20px",
        "border": "none",
    })

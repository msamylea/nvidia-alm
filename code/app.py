import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from components.layout import create_layout
from callbacks import register_callbacks
from utils.configs import app_config
import os
from flask import Flask, request
import requests


server = Flask(__name__)
app = dash.Dash(__name__, 
                server=server,
                external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP], 
                suppress_callback_exceptions=True,
                url_base_pathname=os.environ.get('DASH_URL_BASE_PATHNAME', '/'))

app.layout = create_layout()
register_callbacks(app)

@server.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_to_fastapi(path):
    fastapi_url = f"http://localhost:8000/{path}"
    resp = requests.request(
        method=request.method,
        url=fastapi_url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    response = app.server.make_response(resp.content)
    response.status_code = resp.status_code
    for name, value in headers:
        response.headers[name] = value
    return response

if __name__ == '__main__':
    app.run(debug=app_config['DEBUG'], host=app_config['HOST'], port=8050)

import dash
import dash_bootstrap_components as dbc
from components.layout import create_layout
from callbacks import register_callbacks
from utils.configs import app_config
from flask import Flask, request
import requests
import os

def get_base_pathname():
    proxy_prefix = os.getenv('PROXY_PREFIX', '/projects/nvidia-alm/applications/dash-app')
    if not proxy_prefix.endswith('/'):
        proxy_prefix += '/'
    return proxy_prefix

server = Flask(__name__)
app = dash.Dash(__name__, 
                server=server,
                external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP], 
                suppress_callback_exceptions=True,
                url_base_pathname=get_base_pathname())

app.layout = create_layout()
register_callbacks(app)

@server.route('/projects/nvidia-alm/applications/dash-app/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_to_fastapi(path):
    path = path.rstrip('/')
    fastapi_url = f"http://localhost:8000/{path}"
    

    try:
        resp = requests.request(
            method=request.method,
            url=fastapi_url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False)
        
        # Handle response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        response = app.server.make_response(resp.content)
        response.status_code = resp.status_code
        
        for name, value in headers:
            response.headers[name] = value
            
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error proxying request: {str(e)}")  # Debug logging
        return app.server.make_response(
            {'error': f'Failed to connect to FastAPI backend: {str(e)}'}, 
            502
        )

if __name__ == '__main__':
    print(f"Starting Dash app with base pathname: {get_base_pathname()}")  # Debug logging
    app.run(debug=app_config['DEBUG'], host='0.0.0.0', port=10000)
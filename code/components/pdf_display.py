from dash import html
import sys
import os
import base64
import dash_bootstrap_components as dbc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_pdf_display(pdf_buffer):
    """
    Generates an HTML component to display a PDF from a given buffer.

    Args:
        pdf_buffer (io.BytesIO): A buffer containing the PDF data.

    Returns:
        html.Div: A Dash HTML component containing an iframe that displays the PDF.
    """
    try:
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        report = f"data:application/pdf;base64,{pdf_base64}"

    except Exception as e:
        report = "<h1>Error generating report</h1>"

    pdf_frame = html.Div([
        dbc.Card([
            html.Iframe(
                src=report,
                style={'width': '100%', 'height': '600px'}
            )
        ])
    ])

    return pdf_frame
from dash import html
import sys
import os
import base64
import dash_bootstrap_components as dbc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import traceback
import logging

# Set up logging
logging.basicConfig(
    filename='/project/code/app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('pdf_display')

def create_pdf_display(pdf_buffer):
    """
    Generates an HTML component to display a PDF from a given buffer.

    Args:
        pdf_buffer (io.BytesIO): A buffer containing the PDF data.

    Returns:
        html.Div: A Dash HTML component containing an iframe that displays the PDF.
    """
    logger.info("Starting PDF display creation...")
    logger.info(f"PDF Buffer type: {type(pdf_buffer)}")
    
    try:
        # Get proxy prefix
        proxy_prefix = os.getenv('PROXY_PREFIX', '/projects/nvidia-alm/applications/dash-app').rstrip('/')
        logger.info(f"Proxy prefix: {proxy_prefix}")
        
        # Validate PDF buffer
        if pdf_buffer is None:
            logger.error("PDF buffer is None!")
            raise ValueError("PDF buffer is None")
            
        # Convert PDF to base64
        pdf_bytes = pdf_buffer.getvalue()
        logger.info(f"PDF bytes size: {len(pdf_bytes) if pdf_bytes else 0}")
        
        if not pdf_bytes:
            logger.error("PDF buffer is empty!")
            raise ValueError("PDF buffer is empty")
            
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        logger.info(f"Base64 PDF size: {len(pdf_base64)}")
        
        # Create the data URL for the PDF
        report = f"data:application/pdf;base64,{pdf_base64}"
        logger.info("PDF successfully converted to data URL")

        # Create and return the display component
        display_component = html.Div([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Generated Report", className="mb-0")
                ]),
                dbc.CardBody([
                    html.Iframe(
                        src=report,
                        style={
                            'width': '100%',
                            'height': '800px',
                            'border': 'none',
                            'margin': '0',
                            'padding': '0'
                        }
                    )
                ], style={'padding': '0'})
            ], className="mt-3")
        ], style={'width': '100%', 'margin': '20px 0'})
        
        logger.info("Display component created successfully")
        return display_component

    except Exception as e:
        error_msg = f"Error creating PDF display: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Error Displaying Report", className="text-danger"),
                    html.Pre(str(e)),
                    html.Details([
                        html.Summary("Error Details"),
                        html.Pre(traceback.format_exc())
                    ])
                ])
            ], className="mt-3")
        ])
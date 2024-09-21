from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash
import io
from utils.cache_config import cache, cache_key
from reports.indepth_report import create_final_report
from reports.new_pdf import create_pdf_report
from reports.presentation_report import create_presentation
from utils.utilities import run_async
from utils.report_gen import create_report
from dash import dcc, html
import logging
import traceback
import base64

logger = logging.getLogger(__name__)

async def async_cached_create_final_report(prompt: str, max_samples: int = 10000):
    return await create_final_report(prompt, max_samples=max_samples)

def register_report_callbacks(app):
    @app.callback(
        Output("analysis-output", "children"),
        Output('report-data', 'data'),
        Input("llm-submit-prompt", "n_clicks"),
        State("llm-prompt", "value"),
        State('stored-data', 'data'),
    )
    def generate_report(n_clicks, prompt, stored_data):
        if n_clicks is None or prompt is None or stored_data is None:
            raise PreventUpdate

        # Retrieve the dataframe from the cache
        df = cache.get('current_df')
        
        if df is None:
            raise PreventUpdate("Data not found in cache. Please reload the data.")
        
        report_title, section_results, end_matter, presentation_content = run_async(async_cached_create_final_report(prompt, max_samples=10000))
        
        report = create_report(report_title, section_results, end_matter)
        
        report_data = {
            'report_title': presentation_content['report_title'],
            'section_title': presentation_content['section_title'],
            'section_results': [
                (name, (content, plot.to_dict() if plot else None, plot_config))
                for name, (content, plot, plot_config) in section_results
            ],
            'end_matter': end_matter
        }
        return report, report_data
    
    @app.callback(
    Output("open-pdf-modal", "data"),
    Input("btn-open-pdf-modal", "n_clicks"),
    prevent_initial_call=True
    )
    def set_open_pdf_modal(n_clicks):
        if n_clicks:
            return True
        return dash.no_update

    @app.callback(
        Output("pdf-modal", "is_open"),
        Input("open-pdf-modal", "data"),
        Input("submit-pdf", "n_clicks"),
        State("pdf-modal", "is_open"),
    )
    def toggle_pdf_modal(open_modal, submit_clicks, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "open-pdf-modal" and open_modal:
            return True
        elif prop_id == "submit-pdf":
            return False
        return is_open

    @app.callback(
    Output("download-pdf", "data"),
    Input("submit-pdf", "n_clicks"),
    State('report-data', 'data'),
    State("uploaded-logo", "contents"),
    State("primary-color-picker", "value"),
    State("accent-color-picker", "value"),
    prevent_initial_call=True,
    )
    def generate_pdf(n_clicks, report_data, logo, primary_color, accent_color):
        if n_clicks is None or report_data is None:
            raise PreventUpdate

        try:
            report_title = report_data['report_title']
            section_results = report_data['section_results']
            end_matter = report_data['end_matter']

            # Process the logo
            if logo:
                # The logo is in base64 format, so we need to decode it
                logo_type, logo_string = logo.split(',')
                logo_bytes = base64.b64decode(logo_string)
            else:
                logo_bytes = None

            # Process colors
            primary_color = primary_color.lstrip('#')
            accent_color = accent_color.lstrip('#')

            # Generate the PDF
            pdf_buffer = create_pdf_report(
                report_title, 
                section_results, 
                end_matter, 
                logo_bytes, 
                primary_color, 
                accent_color 
            )

            logger.debug("PDF generation completed")
            return dcc.send_bytes(pdf_buffer.getvalue(), f"{report_title}.pdf")

        except Exception as e:
            logger.error(f"Error in PDF generation: {str(e)}")
            logger.error(traceback.format_exc())
        return None
            
    @app.callback(
        Output("presentation-modal", "is_open"),
        Input("btn-download-pptx", "n_clicks"),
        Input("download_pptx", "n_clicks"),
        State("presentation-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_presentation_modal(open_clicks, download_clicks, modal_is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return modal_is_open
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "btn-download-pptx" and open_clicks:
            return not modal_is_open  # Toggle the modal state
        elif button_id == "download_pptx":
            return False  # Close the modal after generating the PPTX
        return modal_is_open

    @app.callback(
        Output("download-pptx", "data"),
        Input("download_pptx", "n_clicks"),
        State('report-data', 'data'),
        State('ppt-theme-choices', 'value'),
        prevent_initial_call=True,
    )
    def generate_pptx(download_clicks, report_data, selected_template):
        if download_clicks is None or report_data is None:
            raise PreventUpdate

        try:
            selected_template = selected_template or 'default'
            report_title = report_data['report_title']
            section_results = report_data['section_results']
            section_title = report_data['section_title']

            prs = None
            for name, (content, plot_dict, plot_config) in section_results:
                section_content = {
                    "report_title": report_title,
                    section_title: section_title,
                    "content": content,
                    "plot": plot_dict
                }
                logger.debug(f"Processing section: {name}")
                prs = create_presentation(section_content, prs, selected_template)

            # Save the presentation to a buffer
            buffer = io.BytesIO()
            prs.save(buffer)
            buffer.seek(0)

            logger.debug("PPTX generation completed")
            return dcc.send_bytes(buffer.getvalue(), f"{report_title}.pptx")

        except Exception as e:
            logger.error(f"Error in PPTX generation: {str(e)}")
            logger.error(traceback.format_exc())
            return None
from dash.exceptions import PreventUpdate
import dash
import io
from reports.new_pdf import create_pdf_report
from reports.presentation_report import create_presentation
from dash import dcc, html, Input, Output, State, callback_context, ALL
import logging
import traceback
import base64
import dash
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import html, no_update
import asyncio
from utils.utilities import run_async_in_sync
from reports.create_sections import write_section_async, get_outline, write_recommendations_conclusions_async, summarize_section_async
from components.section_content_modal import create_section_modal_body
from plots.plot_factory import parse_llm_response
from components.pdf_display import create_pdf_display  # Import the create_pdf_display function

logger = logging.getLogger(__name__)

def register_report_callbacks(app):
        
    @app.callback(
    Output("section-modal", "is_open"),
    Output("section-modal-content", "children"),
    Output("outline-data", "data"),
    Output("report-generation-trigger", "data"),
    Input("btn-open-pdf-modal", "n_clicks"),
    Input("submit-sections", "n_clicks"),
    Input("cancel-sections", "n_clicks"),
    State("llm-prompt", "value"),
    State("outline-data", "data"),
    State({"type": "section-input", "index": ALL}, "value"),
    State({"type": "section-checkbox", "index": ALL}, "value"),
    prevent_initial_call=True
    )
    def handle_section_modal(open_clicks, submit_clicks, cancel_clicks, prompt, outline_data, section_inputs, section_checkboxes):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "btn-open-pdf-modal" and open_clicks:
            report_title, section_names, num_sections = run_async_in_sync(get_outline(prompt))
            outline_data = {
                "report_title": report_title,
                "sections": [{"name": name, "selected": True} for name in section_names]
            }
            modal_body = create_section_modal_body(outline_data)
            return True, modal_body, outline_data, False
        
        elif button_id == "submit-sections" and submit_clicks:
            if outline_data is None or prompt is None:
                raise PreventUpdate
            
            outline_data = outline_data.copy()
            outline_data["sections"] = outline_data.get("sections", [])
            
            if section_inputs and len(section_inputs) > 0:
                outline_data["report_title"] = section_inputs[0]
                for i, checked in enumerate(section_checkboxes):
                    if i < len(outline_data["sections"]):
                        if checked is not None:
                            outline_data["sections"][i]["selected"] = checked
                new_section = section_inputs[-1] if len(section_inputs) > 1 else None
                if new_section:
                    outline_data["sections"].append({"name": new_section, "selected": True})
            
            return False, None, outline_data, True
        
        elif button_id == "cancel-sections":
            return False, None, None, False
        
        return no_update, no_update, no_update, no_update

    @app.callback(
    Output("analysis-output", "children"),
    Output('report-data', 'data'),
    Output('pdf-buffer', 'data'),  
    Output("report-generated", "data"),
    Input("report-generation-trigger", "data"),
    State("llm-prompt", "value"),
    State("outline-data", "data"),
    State('report-style-data', 'data'),
    prevent_initial_call=True
    )
    def generate_report(trigger, prompt, outline_data, report_style_data):
        if not trigger or outline_data is None or prompt is None:
            raise PreventUpdate

        selected_sections = [section["name"] for section in outline_data["sections"] if section.get("selected", False)]

        async def generate_sections():
            section_tasks = [write_section_async(section_name, prompt) for section_name in selected_sections]
            section_results = await asyncio.gather(*section_tasks)
            
            # Process each section result
            processed_results = []
            for section_name, section_content in section_results:
                plot, plot_data, plot_config = await parse_llm_response(section_name, max_samples=10000)
                processed_results.append((section_name, (section_content, plot, plot_config)))
            
            summarized_sections = [(name, await summarize_section_async(content)) for name, (content, _, _) in processed_results]
            end_matter = await write_recommendations_conclusions_async(summarized_sections)
            return processed_results, end_matter

        section_results, end_matter = run_async_in_sync(generate_sections())

        report_data = {
            'report_title': outline_data["report_title"],
            'section_title': selected_sections[-1] if selected_sections else "",
            'section_results': [
                (name, (content, plot.to_dict() if plot else None, plot_config))
                for name, (content, plot, plot_config) in section_results
            ],
            'end_matter': end_matter
        }
        
        try:
            report_title = report_data['report_title']
            section_results = report_data['section_results']
            end_matter = report_data['end_matter']

            logo = report_style_data.get('logo') if report_style_data else None
            primary_color = report_style_data.get('primary_color', '#1a73e8') if report_style_data else '#1a73e8'
            accent_color = report_style_data.get('accent_color', '#fbbc04') if report_style_data else '#fbbc04'
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
        except Exception as e:
            return html.Div("Error processing report data"), None, None, False

        try:
            pdf_buffer = create_pdf_report(
                report_data['report_title'], 
                report_data['section_results'], 
                report_data['end_matter'], 
                logo_bytes,
                primary_color,
                accent_color
            )
            pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
            pdf_frame = create_pdf_display(pdf_buffer)
        except Exception as e:
            pdf_frame = html.Div("Error generating PDF")
            pdf_base64 = None

        return pdf_frame, report_data, pdf_base64, True
    

    @app.callback(
    Output('report-style-data', 'data'),
    Input('uploaded-logo', 'contents'),
    Input('primary-color-picker', 'value'),
    Input('accent-color-picker', 'value'),
    prevent_initial_call=True
    )
    def update_report_style(logo, primary_color, accent_color):
        return {
            'logo': logo,
            'primary_color': primary_color,
            'accent_color': accent_color
        }
        
    @app.callback(
        Output("download-pptx", "disabled"),  
        Input("report-generated", "data")
    )
    def toggle_download_button(report_generated):
        if report_generated:
            return False   
        return True  
    
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
            return not modal_is_open 
        elif button_id == "download_pptx":
            return False  
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
            print(f"Error in PPTX generation: {str(e)}")
            print(traceback.format_exc())
            return None
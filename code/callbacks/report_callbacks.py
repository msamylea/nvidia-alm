from dash.exceptions import PreventUpdate
import dash
import io
import plotly.graph_objects as go
import plotly.express as px
from reports.pdf.new_pdf import create_pdf_report
from reports.pptx.presentation_report import create_presentation
from dash import dcc, html, Input, Output, State, callback_context, ALL
import traceback
import base64
import dash
from dash import html, no_update

import asyncio
from utils.utilities import run_async_in_sync
from plotly.io import to_image
from reports.backend.create_sections import write_section_async, get_outline, write_recommendations_conclusions_async, summarize_section_async
from plots.plot_factory import parse_llm_response
from components.pdf_gen_options_modal import create_section_modal_body
from components.pdf_display import create_pdf_display  
import logging

logging.basicConfig(
    filename='/project/code/app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('report_callback')

def register_report_callbacks(app):
        
    @app.callback(
    Output("error-toast", "is_open"),
    Output("error-message", "children"),
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
    State("stored-data", "data"),
    prevent_initial_call=True
    )
    def handle_section_modal(open_clicks, submit_clicks, cancel_clicks, prompt, outline_data, section_inputs, section_checkboxes, stored_data):
        """
        Handle the logic for opening, submitting, and canceling the section modal in a report generation application.
        Parameters:
        open_clicks (int): Number of times the open button has been clicked.
        submit_clicks (int): Number of times the submit button has been clicked.
        cancel_clicks (int): Number of times the cancel button has been clicked.
        prompt (str): The query entered by the user to generate a report.
        outline_data (dict): Data structure containing the report outline.
        section_inputs (list): List of inputs for section titles.
        section_checkboxes (list): List of checkboxes indicating selected sections.
        stored_data (any): Data uploaded by the user.
        Returns:
        tuple: A tuple containing updates for error status, error message, modal visibility, modal body, outline data, and a flag indicating if the modal was submitted.
        """
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "btn-open-pdf-modal" and open_clicks:
            if prompt is None and stored_data is None:
                error = True
                error_message = "Upload a dataset and enter a query to begin."
                return error, error_message, no_update, no_update, no_update, no_update
            
            elif stored_data is None:
                error = True
                error_message = "Please upload data to generate a report."
                
                return error, error_message, no_update, no_update, no_update, no_update
            elif prompt is None:
                error = True
                error_message = "Please enter a query to generate a report."
                return error, error_message, no_update, no_update, no_update, no_update
            
            report_title, section_names, num_sections = run_async_in_sync(get_outline(prompt))
            outline_data = {
                "report_title": report_title,
                "sections": [{"name": name, "selected": True} for name in section_names]
            }
            modal_body = create_section_modal_body(outline_data)
            return no_update, no_update, True, modal_body, outline_data, False
        
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
            
            return no_update, no_update,False, None, outline_data, True
        
        elif button_id == "cancel-sections":
            return no_update, no_update,False, None, None, False
        
        return no_update, no_update,no_update, no_update, no_update, no_update

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
        """
        Generates a report based on the provided outline data and report style.
        """
        logger.info("Starting report generation callback...")
        
        if not trigger or outline_data is None or prompt is None:
            logger.warning("Report generation triggered without required data")
            raise PreventUpdate

        try:
            logger.info("Processing selected sections...")
            selected_sections = [section["name"] for section in outline_data["sections"] if section.get("selected", False)]

            async def generate_sections():
                logger.info("Starting section generation...")
                section_tasks = [write_section_async(section_name, prompt) for section_name in selected_sections]
                section_results = await asyncio.gather(*section_tasks)
                
                processed_results = []
                for section_name, section_content in section_results:
                    try:
                        logger.info(f"Processing section: {section_name}")
                        plot, plot_data, plot_config = await parse_llm_response(section_name, max_samples=10000)
                        
                        if plot:
                            try:
                                if isinstance(plot, (go.Figure, px)):
                                    img_bytes = to_image(plot, format="png", engine="kaleido", width=900, height=500, scale=2)
                                    plot_image = base64.b64encode(img_bytes).decode('utf-8')
                                else:
                                    plot_image = None
                            except Exception as img_error:
                                logger.error(f"Error converting plot to image: {str(img_error)}")
                                plot_image = None
                        else:
                            plot_image = None
                                
                        processed_results.append((section_name, (section_content, plot_image, plot_config)))
                    except Exception as e:
                        logger.error(f"Error processing section {section_name}: {str(e)}")
                        logger.error(traceback.format_exc())
                        processed_results.append((section_name, (section_content, None, None)))
                
                logger.info("Summarizing sections...")
                summarized_sections = [(name, await summarize_section_async(content)) for name, (content, _, _) in processed_results]
                end_matter = await write_recommendations_conclusions_async(summarized_sections)
                
                return processed_results, end_matter

            logger.info("Running section generation...")
            section_results, end_matter = run_async_in_sync(generate_sections())

            logger.info("Creating report data structure...")
            report_data = {
                'report_title': outline_data["report_title"],
                'section_title': selected_sections[-1] if selected_sections else "",
                'section_results': [
                    (name, (content, plot_image, plot_config))
                    for name, (content, plot_image, plot_config) in section_results
                ],
                'end_matter': end_matter
            }
            
            # Process report styling
            logger.info("Processing report styling...")
            report_title = report_data['report_title']
            section_results = report_data['section_results']
            end_matter = report_data['end_matter']

            logo = report_style_data.get('logo') if report_style_data else None
            primary_color = report_style_data.get('primary_color', '#1a73e8') if report_style_data else '#1a73e8'
            accent_color = report_style_data.get('accent_color', '#fbbc04') if report_style_data else '#fbbc04'
            company_name = report_style_data.get('company_name', ' Name') if report_style_data else ''
            
            if logo:
                try:
                    logo_type, logo_string = logo.split(',')
                    logo_bytes = base64.b64decode(logo_string)
                    logger.info("Logo processed successfully")
                except Exception as e:
                    logger.error(f"Error processing logo: {str(e)}")
                    logo_bytes = None
            else:
                logo_bytes = None

            primary_color = primary_color.lstrip('#')
            accent_color = accent_color.lstrip('#')

            logger.info("Creating PDF report...")
            try:
                pdf_buffer = create_pdf_report(
                    report_data['report_title'], 
                    report_data['section_results'], 
                    report_data['end_matter'], 
                    logo_bytes,
                    primary_color,
                    accent_color,
                    company_name
                )
                logger.info("PDF report created successfully")
                
                # Check PDF buffer
                if pdf_buffer is None:
                    raise ValueError("PDF buffer is None after creation")
                    
                buffer_size = len(pdf_buffer.getvalue())
                logger.info(f"PDF buffer size: {buffer_size} bytes")
                
            except Exception as e:
                logger.error(f"Error creating PDF report: {str(e)}")
                logger.error(traceback.format_exc())
                raise

            logger.info("Creating PDF display component...")
            pdf_frame = create_pdf_display(pdf_buffer)
            pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

            logger.info("Report generation completed successfully")
            return pdf_frame, report_data, pdf_base64, True

        except Exception as e:
            logger.error(f"Error in report generation: {str(e)}")
            logger.error(traceback.format_exc())
            return html.Div([
                html.H4("Error generating report"),
                html.Pre(str(e)),
                html.Details([
                    html.Summary("Error Details"),
                    html.Pre(traceback.format_exc())
                ])
            ]), None, None, False

    @app.callback(
    Output('report-style-data', 'data'),
    Input('uploaded-logo', 'contents'),
    Input('primary-color-picker', 'value'),
    Input('accent-color-picker', 'value'),
    Input('company-name', 'value'),
    prevent_initial_call=True
    )
    def update_report_style(logo, primary_color, accent_color, company_name):
        """
        Updates the report style with the given parameters.

        Args:
            logo (str): The URL or path to the company's logo.
            primary_color (str): The primary color to be used in the report.
            accent_color (str): The accent color to be used in the report.
            company_name (str): The name of the company. If not provided, defaults to an empty string.

        Returns:
            dict: A dictionary containing the updated report style with keys 'logo', 'primary_color', 'accent_color', and 'company_name'.
        """
        if not company_name:
            company_name = ''
        return {
            'logo': logo,
            'primary_color': primary_color,
            'accent_color': accent_color,
            'company_name': company_name
        }
        
    @app.callback(
        Output("download-pptx", "disabled"),  
        Input("report-generated", "data")
    )
    def toggle_download_button(report_generated):
        """
        Toggles the state of the download button based on whether a report has been generated.

        Args:
            report_generated (bool): A flag indicating if the report has been generated.

        Returns:
            bool: False if the report has been generated (enabling the download button), 
                  True otherwise (disabling the download button).
        """
        if report_generated:
            return False   
        return True  
    
    @app.callback(
        Output("presentation-modal", "is_open"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-toast", "is_open", allow_duplicate=True),
        Input("btn-open-presentation-modal", "n_clicks"),
        Input("download_pptx", "n_clicks"),
        State("presentation-modal", "is_open"),
        State("report-data", "data"),
        prevent_initial_call=True,
    )
    def toggle_presentation_modal(open_clicks, download_clicks, modal_is_open, report_data):
        """
        Toggles the state of the presentation modal based on user interactions.

        Parameters:
        open_clicks (int): Number of times the open modal button has been clicked.
        download_clicks (int): Number of times the download button has been clicked.
        modal_is_open (bool): Current state of the modal (True if open, False if closed).
        report_data (dict or None): Data of the generated report, if any.

        Returns:
        tuple: A tuple containing:
            - bool: New state of the modal (True if open, False if closed).
            - str or None: Error message if any, otherwise None.
            - bool: Indicator if an error message should be displayed (True if error, False otherwise).
        """
        ctx = dash.callback_context
        if not ctx.triggered:
            return modal_is_open
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "btn-open-presentation-modal" and open_clicks:
            if report_data is None:
                error = "You must generate a report before creating a presentation."
                return False, error, True
            return not modal_is_open, None, False 
        elif button_id == "download_pptx":
            return False, None, False  
        return modal_is_open, None, False

    @app.callback(
    Output("download-pptx", "data"),
    Input("download_pptx", "n_clicks"),
    State('report-data', 'data'),
    State('ppt-theme-choices', 'value'),
    prevent_initial_call=True,
    )
    def generate_pptx(download_clicks, report_data, selected_template):
        """
        Generates a PowerPoint presentation based on the provided report data and template.
        Args:
            download_clicks (int): The number of times the download button has been clicked.
            report_data (dict): A dictionary containing the report data, including 'report_title', 
                                'section_results', and 'section_title'.
            selected_template (str): The template to be used for the presentation. Defaults to 'default' if not provided.
        Returns:
            dcc.send_bytes: A Dash component that sends the generated PowerPoint file to the client.
            None: If an exception occurs during the generation process or if required data is missing.
        Raises:
            PreventUpdate: If `download_clicks` or `report_data` is None.
        """
        if download_clicks is None or report_data is None:
            raise PreventUpdate

        try:
            selected_template = selected_template or 'default'
            report_title = report_data['report_title']
            section_results = report_data['section_results']
            section_title = report_data['section_title']

            prs = None
            for name, (content, plot_image, plot_config) in section_results:
                section_content = {
                    "report_title": report_title,
                    "section_title": section_title,
                    "content": content,
                    "plot_image": plot_image
                }
                prs = create_presentation(section_content, prs, selected_template)
            
            buffer = io.BytesIO()
            prs.save(buffer)
            buffer.seek(0)
            return dcc.send_bytes(buffer.getvalue(), f"{report_title}.pptx")
        except Exception as e:
            return None
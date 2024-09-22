# import dash
# from dash.dependencies import Input, Output, State, ALL
# from dash.exceptions import PreventUpdate
# import dash_bootstrap_components as dbc
# from dash import html, no_update
# import asyncio
# from utils.utilities import run_async_in_sync
# from reports.create_sections import write_section_async, get_outline, write_recommendations_conclusions_async, summarize_section_async
# from reports.report_gen import create_report
# from components.section_content_modal import create_section_modal_body
# from plots.plot_factory import parse_llm_response

# def register_section_modal_callbacks(app):
#     @app.callback(
#         Output("section-modal", "is_open"),
#         Output("outline-data", "data"),
#         Output("section-modal-body", "children"),
#         Input("llm-submit-prompt", "n_clicks"),
#         Input("submit-sections", "n_clicks"),
#         Input("cancel-sections", "n_clicks"),
#         State("llm-prompt", "value"),
#         State("outline-data", "data"),
#         State({"type": "section-input", "index": ALL}, "value"),
#         State({"type": "section-checkbox", "index": ALL}, "value"),
#         prevent_initial_call=True
#     )
#     def handle_section_modal(submit_clicks, confirm_clicks, cancel_clicks,
#                              prompt, outline_data, section_inputs, section_checkboxes):
#         ctx = dash.callback_context
#         if not ctx.triggered:
#             raise PreventUpdate

#         button_id = ctx.triggered[0]["prop_id"].split(".")[0]

#         if button_id == "llm-submit-prompt" and submit_clicks:
#             # Get outline from LLM
#             report_title, section_names, num_sections = run_async_in_sync(get_outline(prompt))
#             outline_data = {
#                 "report_title": report_title,
#                 "sections": [{"name": name, "selected": True} for name in section_names]
#             }
            
#             # Create modal body
#             modal_body = create_section_modal_body(outline_data)
            
#             return True, outline_data, modal_body

#         elif button_id == "submit-sections":
#             if outline_data is None or prompt is None:
#                 raise PreventUpdate

#             # Update outline data with user selections
#             if section_inputs and len(section_inputs) > 0:
#                 outline_data["report_title"] = section_inputs[0]  # First input is report title
                
#                 # Update existing sections
#                 for i, checked in enumerate(section_checkboxes):
#                     if i < len(outline_data["sections"]):
#                         if checked is not None:
#                             outline_data["sections"][i]["selected"] = checked
#                         # If checked is None, keep the original selected state
                
#                 # Add new section if provided
#                 new_section = section_inputs[-1] if len(section_inputs) > 1 else None
#                 if new_section:
#                     outline_data["sections"].append({"name": new_section, "selected": True})

#             # Close the modal immediately
#             return False, outline_data, no_update

#         elif button_id == "cancel-sections":
#             # Close the modal and clear the outline data
#             return False, None, no_update

#         return no_update, no_update, no_update

#     @app.callback(
#         Output("analysis-output", "children"),
#         Output('report-data', 'data'),
#         Input("outline-data", "data"),
#         State("llm-prompt", "value"),
#         prevent_initial_call=True
#     )
#     def process_report(outline_data, prompt):
#         if outline_data is None or prompt is None:
#             raise PreventUpdate

#         selected_sections = [section["name"] for section in outline_data["sections"] if section.get("selected", False)]

#         async def generate_sections():
#             section_tasks = [write_section_async(section_name, prompt) for section_name in selected_sections]
#             section_results = await asyncio.gather(*section_tasks)
            
#             # Process each section result
#             processed_results = []
#             for section_name, section_content in section_results:
#                 plot, plot_data, plot_config = await parse_llm_response(section_name, max_samples=10000)
#                 processed_results.append((section_name, (section_content, plot, plot_config)))
            
#             summarized_sections = [(name, await summarize_section_async(content)) for name, (content, _, _) in processed_results]
#             end_matter = await write_recommendations_conclusions_async(summarized_sections)
#             return processed_results, end_matter

#         section_results, end_matter = run_async_in_sync(generate_sections())
        
#         report = create_report(outline_data["report_title"], section_results, end_matter)
        
#         report_data = {
#             'report_title': outline_data["report_title"],
#             'section_title': selected_sections[-1] if selected_sections else "",
#             'section_results': section_results,
#             'end_matter': end_matter
#         }

#         return report, report_data
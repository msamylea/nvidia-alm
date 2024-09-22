from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from utils.utilities import extract_content
from utils.formatting_utilities import preprocess_text, create_ag_grid
import re

def create_report(report_title, section_results, end_matter):
    section_cards = []
    for section_name, section_data in section_results:
        formatted_content = []
        
        if isinstance(section_data, tuple):
            if len(section_data) == 3:
                section_content, plot, plot_config = section_data
            elif len(section_data) == 2:
                section_content, plot = section_data
                plot_config = None
            else:
                section_content = section_data[0]
                plot = None
                plot_config = None
        else:
            section_content = section_data
            plot = None
            plot_config = None
        
        # Ensure section_content is a string
        if not isinstance(section_content, str):
            section_content = str(section_content)
        
        elements = extract_content(section_content)
        for element_type, element in elements:
            if element_type == 'text':
                lines = element.split('\n')
                cleaned_lines = []
                prev_line = ''
                for line in lines:
                    if line.strip() != prev_line.strip():
                        cleaned_lines.append(line)
                    prev_line = line
                cleaned_element = '\n'.join(cleaned_lines)
                
                # Remove section name from the beginning if it exists
                cleaned_element = re.sub(f'^#{1,6}\s*{re.escape(section_name)}\s*\n', '', cleaned_element, flags=re.IGNORECASE)
                preprocessed_element = preprocess_text(cleaned_element)
                formatted_content.append(dcc.Markdown(preprocessed_element, mathjax=True))
            elif element_type == 'table':
                formatted_content.append(create_ag_grid(element))
                if len(element) > 0:
                    formatted_content.append(html.Br())
            elif element_type == 'code':
                formatted_content.append(dcc.Markdown(f"```\n{element}\n```", mathjax=True))
        
        if plot:
            if isinstance(plot, dict) and 'data' in plot and 'layout' in plot:
                figure = go.Figure(data=plot['data'], layout=plot['layout'])
            elif isinstance(plot, go.Figure):
                figure = plot
            else:
                figure = None
            
            if figure:
                plot_description = "This plot shows the data visualization for this section."
                if plot_config:
                    if 'x' in plot_config and 'y' in plot_config:
                        plot_description = f"This plot shows {plot_config['x']} vs {plot_config['y']}"
                    if 'color' in plot_config:
                        plot_description += f", colored by {plot_config['color']}"
                    if 'size' in plot_config:
                        plot_description += f", with size representing {plot_config['size']}"
                
                formatted_content.append(dcc.Markdown(preprocess_text(plot_description)))
                formatted_content.append(dcc.Graph(figure=figure))
        
        section_card = dbc.Card([
            dbc.CardHeader(html.H4(section_name, className="report-card-header")),
            dbc.CardBody(formatted_content, className="report-card-body")
        ], className="report-card")
        
        section_cards.append(section_card)
        section_cards.append(html.Br())
    
    # Process end matter
    end_elements = extract_content(end_matter)
    formatted_end_content = []
    for element_type, element in end_elements:
        if element_type == 'text':
            lines = element.split('\n')
            cleaned_lines = []
            prev_line = ''
            for line in lines:
                if line.strip() != prev_line.strip():
                    cleaned_lines.append(line)
                prev_line = line
            cleaned_element = '\n'.join(cleaned_lines)
            
            preprocessed_element = preprocess_text(cleaned_element)
            formatted_end_content.append(dcc.Markdown(preprocessed_element))
        elif element_type == 'table':
            formatted_end_content.append(create_ag_grid(element))
        elif element_type == 'code':
            formatted_end_content.append(dcc.Markdown(f"```\n{element}\n```"))
    
    end_matter_card = dbc.Card([
        dbc.CardHeader(html.H4("Conclusion and Recommendations", className="report-card-header")),
        dbc.CardBody(formatted_end_content, className="report-card-body"),
        html.Br(),
    ], className="report-card")
    
    return html.Div([
        html.Br(),
        dbc.Container([
            dbc.Card([
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dcc.Loading([
                                    dbc.Button("Download PPTX", id="btn-download-pptx", color="primary", className="custom-btn"),
                                    dcc.Download(id="download-pptx")
                                ], className="d-flex justify-content-center align-items-center"),
                            ], width="auto"),
                            dbc.Col([
                                dcc.Loading([    
                                    dbc.Button("Download PDF", id="btn-open-pdf-modal", color="primary", className="custom-btn"),
                                    dcc.Download(id="download-pdf")
                                ], className="d-flex justify-content-center align-items-center"),
                            ], width="auto")
                        ], className="justify-content-center"),
                        html.Br(),
                        html.H2(report_title, className="text-center"),
                        html.Br(),
                        html.Div(section_cards, className="report-card"),
                        html.Hr(style={'margin': '30px 0'}),
                        html.Div(end_matter_card, className="report-card")
                    ], width={"size": 10, "offset": 1})
                ])
            ], className="report-buttons-card")
        ], fluid=True),
    ])
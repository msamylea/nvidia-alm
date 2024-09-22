from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from utils.utilities import extract_content
from utils.formatting_utilities import preprocess_text, create_ag_grid
import re

def create_report(report_title, section_results, end_matter):
    section_cards = []
    for section_name, (section_content, plot, plot_config) in section_results:
        formatted_content = []
        
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
                preprocessed_element = preprocess_text(element)
                formatted_content.append(dcc.Markdown(preprocessed_element, mathjax=True))
            elif element_type == 'table':
                formatted_content.append(create_ag_grid(element))
                if len(element) == 0:
                    pass
                else:
                    formatted_content.append(html.Br())
            elif element_type == 'code':
                formatted_content.append(dcc.Markdown(f"```\n{element}\n```", mathjax=True))
        
        if plot:
            plot_description = preprocess_text(f"This plot shows {plot_config.get('x', 'X')} vs {plot_config.get('y', 'Y')}")
            if plot_config.get('color'):
                plot_description += preprocess_text(f", colored by {plot_config['color']}")
            if plot_config.get('size'):
                plot_description += preprocess_text(f", with size representing {plot_config['size']}")
            
            formatted_content.append(dcc.Markdown(plot_description))
            formatted_content.append(dcc.Graph(figure=plot))
        
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
            
            # Remove section name from the beginning if it exists
            cleaned_element = re.sub(f'^#{1,6}\s*{re.escape(section_name)}\s*\n', '', cleaned_element, flags=re.IGNORECASE)
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
                    html.Div(section_cards, className="report-card"),
                    html.Hr(style={'margin': '30px 0'}),
                    html.Div(end_matter_card, className="report-card")
                ], width={"size": 10, "offset": 1})
            ])
        ], className="report-buttons-card")
    ], fluid=True),
    ])
    

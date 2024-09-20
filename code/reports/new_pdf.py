from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import markdown
from bs4 import BeautifulSoup
import io
from utils.utilities import extract_content
import plotly.graph_objects as go
from PIL import Image

def report_markdown(md_text):
    html = markdown.markdown(md_text)

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    elements = []
    
    for elem in soup:
        if elem.name is None:  # This is a NavigableString
            continue
        
        text_content = elem.get_text() or ""  # Ensure text content is not None
        if elem.name == 'p':
            elements.append(text_content)
            elements.append('<br> <br> </br> </br>')  # Add space after paragraph
        elif elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            style_name = f'Heading{elem.name[1]}'
            elements.append(text_content)
            elements.append('<br> <br> </br> </br>')  # Add more space after headings
        elif elem.name == 'ul':
            for li in elem.find_all('li'):
                bullet_text = f"• {li.get_text() or ''}"
                elements.append(bullet_text)
            elements.append('<br> <br> </br> </br>')  # Add space after list
        elif elem.name == 'ol':
            for i, li in enumerate(elem.find_all('li'), 1):
                number_text = f"{i}. {li.get_text() or ''}"
                elements.append(number_text)
            elements.append('<br> <br> </br> </br>')  
            
    return elements
        

def create_pdf(report_title, section_results, end_matter, output_buffer):
    for section_name, (section_content, plot_dict, plot_config) in section_results:
        elements = extract_content(section_content)
        elements = []
        text = []
        
        last_heading = None
        for element_type, element in elements:
            if element_type == 'text':
                parsed_elements = report_markdown(element)
                for parsed_element in parsed_elements:
                    if isinstance(parsed_element):
                        # Check for duplicate headings
                        if parsed_element.style.name.startswith('Heading') and parsed_element.text == last_heading:
                            continue
                        last_heading = parsed_element.text
                    text.append(parsed_element)
            elif element_type == 'table':
                if isinstance(element, str):
                    # If element is a string, parse it
                    rows = [row.strip() for row in element.split('\n') if row.strip()]
                    headers = [cell.strip() for cell in rows[0].split('|') if cell.strip()]
                    table_data = [headers]
                    for row in rows[2:]:  # Skip the header separator row
                        cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                        if len(cells) == len(headers):
                            table_data.append(cells)
                elif isinstance(element, dict):
                    # If element is already a dictionary, use it as is
                    table_data = [element['columns']] + element['data']
                else:
                    # If element is neither string nor dict, skip it
                    continue
            if plot_dict is not None:
                # Convert Plotly figure to static image
                plot = go.Figure(data=plot_dict['data'], layout=plot_dict['layout'])
                img_buffer = io.BytesIO()
                plot.write_image(img_buffer, format="png", width=600, height=400)
                img_buffer.seek(0)
                img = Image(img_buffer)
                # Add plot description
                plot_description = f"<b><center>Figure: {plot_config.get('x', 'X')} vs {plot_config.get('y', 'Y')}"
                if plot_config.get('color'):
                    plot_description += f", colored by {plot_config['color']}"
                if plot_config.get('size'):
                    plot_description += f", with size representing {plot_config['size']}"
                plot_description += "</center></b>"
                
        pdf = text + table_data + img + plot_description
        

        html = HTML(string=pdf)

        css = """
        h1 {
            font-size: 16px;
            font-weight: bold;
        }
        h2 {
            font-size: 14px;
            font-weight: bold;
        }
        h3 {
            font-size: 12px;
            font-weight: bold;
        }
        h4 {
            font-size: 10px;
            font-weight: bold;
        }
        p {
            font-size: 10px;
        }
        ul {
            font-size: 10px;
        }
        ol {
            font-size: 10px;
        }
        """
        
    font_config = FontConfiguration()

    html.write_pdf(
        '/tmp/example.pdf', stylesheets=[css],
        font_config=font_config)
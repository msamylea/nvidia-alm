from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import markdown
import base64
from jinja2 import Template
import io
from datetime import datetime
from bs4 import BeautifulSoup
from utils.utilities import extract_content
import pandas as pd

def process_tables(md_content):
    """
    Processes markdown content to extract and convert tables into HTML format.

    Args:
        md_content (str): The markdown content containing tables to be processed.

    Returns:
        list: A list of HTML table strings.

    The function performs the following steps:
    1. Sets the pandas display option for maximum column width.
    2. Extracts elements from the markdown content.
    3. Iterates through the extracted elements to identify and process tables.
    4. For string-based tables, it parses the table rows and headers.
    5. For dictionary-based tables, it directly uses the columns and data.
    6. Cleans the table data by removing markdown bold syntax.
    7. Converts the table data into a pandas DataFrame.
    8. Formats numeric values to two decimal places.
    9. Converts the DataFrame to an HTML table with specific classes and without escaping HTML characters.
    10. Appends the HTML table to the list of processed tables.

    Note:
        - The function assumes that the first row of a string-based table contains headers.
        - Rows are split by newline characters, and cells are split by the '|' character.
        - The function handles both string and dictionary representations of tables.
    """
    pd.set_option('display.max_colwidth', 0)
    elements = extract_content(md_content)
    processed_tables = []

    for element_type, element in elements:
        if element_type == 'table':
            if isinstance(element, str):
                rows = [row.strip() for row in element.split('\n') if row.strip()]
                headers = [cell.strip() for cell in rows[0].split('|') if cell.strip()]
                table_data = [headers]
                for row in rows[2:]:
                    cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                    if len(cells) == len(headers):
                        table_data.append(cells)
            elif isinstance(element, dict):
                table_data = [element['columns']] + element['data']

            table_data = [[cell.replace('**', '') for cell in row] for row in table_data]
            df = pd.DataFrame(table_data[1:], columns=table_data[0])
            df = df.map(lambda x: f"{float(x):.2f}" if x.replace('.', '', 1).isdigit() else x)
            html_table = df.to_html(index=False, classes=['table', 'table-striped', 'table-bordered'], escape=False)
            processed_tables.append(html_table)

    return processed_tables

def convert_markdown_to_html(md_content, section_title):
    """
    Converts Markdown content to HTML with additional processing for tables and specific HTML elements.
    Args:
        md_content (str): The Markdown content to be converted.
        section_title (str): The title of the section being processed.
    Returns:
        str: The processed HTML content as a string.
    The function performs the following steps:
    1. Processes tables within the Markdown content.
    2. Converts the Markdown content to HTML using the `markdown` library with specific extensions.
    3. Uses BeautifulSoup to parse the HTML content and perform additional processing:
        - Adds specific classes to headers (h2 to h6) to ensure unique headers.
        - Removes all h1 headers.
        - Adds 'list-unstyled' class to all unordered (ul) and ordered (ol) lists.
        - Adds 'paragraph' class to all paragraph (p) tags.
        - Adds 'code-block' class to all preformatted (pre) tags.
        - Adds 'inline-code' class to all inline code (code) tags that are not within pre tags.
        - Adds 'bold-text' class to all strong and b tags.
        - Adds 'italic-text' class to all em and i tags.
    4. Replaces table tags in the HTML content with processed tables.
    Note:
        The function assumes that the `process_tables` function and the `markdown` and `BeautifulSoup` libraries are available in the scope.
    """
    processed_tables = process_tables(md_content)
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'sane_lists', 'smarty', 'toc'])
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    seen_headers = set()
    for i in range(2, 7):  # h2 to h6, skip h1
        for header in soup.find_all(f'h{i}'):
            header_text = header.get_text(strip=True).lower()
            if header_text not in seen_headers:
                seen_headers.add(header_text)
                header['class'] = header.get('class', []) + [f'header-{i}']
            else:
                header.decompose()  
                
    for header in soup.find_all('h1'):
        header.decompose()
        
    for ul in soup.find_all('ul'):
        ul['class'] = ul.get('class', []) + ['list-unstyled']
    
    for ol in soup.find_all('ol'):
        ol['class'] = ol.get('class', []) + ['list-unstyled']
    
    for p in soup.find_all('p'):
        p['class'] = p.get('class', []) + ['paragraph']
    
    for pre in soup.find_all('pre'):
        pre['class'] = pre.get('class', []) + ['code-block']
    
    for code in soup.find_all('code'):
        if code.parent.name != 'pre':
            code['class'] = code.get('class', []) + ['inline-code']
    
    for strong in soup.find_all(['strong', 'b']):
        strong['class'] = strong.get('class', []) + ['bold-text']
    
    for em in soup.find_all(['em', 'i']):
        em['class'] = em.get('class', []) + ['italic-text']
    
    table_tags = soup.find_all('table')
    for i, table_tag in enumerate(table_tags):
        if i < len(processed_tables):
            new_table = BeautifulSoup(processed_tables[i], 'html.parser')
            table_tag.replace_with(new_table)
    
    return str(soup)

def generate_toc(sections):
    """
    Generates a table of contents (TOC) in HTML format from a list of sections.

    Args:
        sections (list of dict): A list of dictionaries where each dictionary represents a section.
                                 Each dictionary must have an "id" key with a unique identifier for the section.

    Returns:
        str: A string containing the HTML for the table of contents.

    Example:
        sections = [
            {"id": "introduction"},
            {"id": "chapter1"},
            {"id": "chapter2"}
        ]
        toc_html = generate_toc(sections)
        # toc_html will be:
        # '<ul><li><a href="#introduction"></a></li><li><a href="#chapter1"></a></li><li><a href="#chapter2"></a></li></ul>'
    """
    toc_html = '<ul>'
    seen_ids = set()
    for section in sections:
        section_id = section["id"]
        original_id = section_id
        counter = 1
        while section_id in seen_ids:
            section_id = f"{original_id}-{counter}"
            counter += 1
        seen_ids.add(section_id)
        toc_html += f'<li><a href="#{section_id}"></a></li>'
    toc_html += '</ul>'
    return toc_html

def create_pdf_report(report_title, section_results, end_matter, logo_bytes, primary_color, accent_color, company_name):
    """
    Generates a PDF report with the given parameters.
    Args:
        report_title (str): The title of the report.
        section_results (list): A list of tuples containing section names, content, plot images, and plot configurations.
        end_matter (str): The concluding content of the report.
        logo_bytes (bytes): The logo image in bytes.
        primary_color (str): The primary color for the report's styling.
        accent_color (str): The accent color for the report's styling.
        company_name (str): The name of the company to be included in the report.
    Returns:
        io.BytesIO: A buffer containing the generated PDF report.
    """
    with open('reports/pdf/pdf_report.css', 'r') as file:
        css_template = file.read()
    
    css = css_template.replace("{primary_color}", primary_color).replace("{accent_color}", accent_color).replace("{company_name}", company_name).replace("{report_title}", report_title)
    
    html_template = Template("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{{ report_title }}</title>
        <style>
            {{ css }}
        </style>
    </head>
    <body>
        <div class="cover">
            <div class="layout">
                <div class="top-section">
                    <div class="logo-container">
                        {% if logo %}
                        <img src="data:image/png;base64,{{ logo }}" alt="Logo" class="logo">
                        {% endif %}
                    </div>
                </div>
                <h1>{{ report_title }}</h1>
                <p class="date">{{ generated_date }}</p>
            </div>
        </div>
        
        <div class="content-start"></div>
        
        <article id="contents">
            <h2>Table of Contents</h2>
            {{ toc | safe }}
        </article>
        
        <article id="sections">
            {% for section in sections %}
            <div class="section">
                <h2 id="{{ section.id }}">{{ section.number }} {{ section.title }}</h2>
                {{ section.content | safe }}
                {% if section.plot %}
                <img src="data:image/png;base64,{{ section.plot }}" alt="Plot" class="plot">
                {{ section.plot_description | safe }}
                {% endif %}
            </div>
            {% endfor %}
        </article>
        
        <article id="conclusion">
            <h2>Conclusion and Recommendations</h2>
            {{ end_matter | safe }}
        </article>
    </body>
    </html>
    """)
    
    processed_sections = []
    for index, (section_name, (section_content, plot_image, plot_config)) in enumerate(section_results, start=1):
        section_id = section_name.lower().replace(" ", "-")
        html_content = convert_markdown_to_html(section_content, section_name)
        
        plot_description = ""
        if plot_image:
            plot_description = f"Figure {index}: {plot_config.get('x', 'X')} vs {plot_config.get('y', 'Y')}"
            if plot_config.get('color'):
                plot_description += f", colored by {plot_config['color']}"
            if plot_config.get('size'):
                plot_description += f", with size represented by {plot_config['size']}"
            
            plot_description = f'<div class="caption">{plot_description}</div>'
    
        processed_sections.append({
            'id': section_id,
            'number': index,
            'title': section_name,
            'content': html_content,
            'plot': plot_image,
            'plot_description': plot_description
        })
    
    toc_html = generate_toc(processed_sections)
    end_matter_html = convert_markdown_to_html(end_matter, "End Matter")
    
    html_content = html_template.render(
        report_title=report_title,
        logo=base64.b64encode(logo_bytes).decode('utf-8') if logo_bytes else None,
        generated_date=datetime.now().strftime('%m-%d-%Y'),
        sections=processed_sections,
        end_matter=end_matter_html,
        css=css,
        toc=toc_html
    )
    
    font_config = FontConfiguration()
    html = HTML(string=html_content)
    css = CSS(string=css)
    
    pdf_buffer = io.BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css], font_config=font_config)
    pdf_buffer.seek(0)
    
    return pdf_buffer
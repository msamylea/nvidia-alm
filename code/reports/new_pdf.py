from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import markdown
import base64
from jinja2 import Template
import plotly.graph_objects as go
import plotly.io as pio
import io
from datetime import datetime
from bs4 import BeautifulSoup
from utils.utilities import extract_content
import pandas as pd

def process_tables(md_content):
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
    processed_tables = process_tables(md_content)
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'sane_lists', 'smarty', 'toc'])
    
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    seen_headers = set()
    for i in range(2, 7):  # h2 to h6, skip h1
        for header in soup.find_all(f'h{i}'):
            header_text = header.get_text(strip=True).lower()
            if header_text not in seen_headers:
                seen_headers.add(header_text)
                header['class'] = header.get('class', []) + [f'header-{i}']
            else:
                header.decompose()  # Remove duplicate header
                
    for header in soup.find_all('h1'):
        header.decompose()
        
    # Process lists
    for ul in soup.find_all('ul'):
        ul['class'] = ul.get('class', []) + ['list-unstyled']
    
    for ol in soup.find_all('ol'):
        ol['class'] = ol.get('class', []) + ['list-unstyled']
    
    # Process paragraphs
    for p in soup.find_all('p'):
        p['class'] = p.get('class', []) + ['paragraph']
    
    # Process code blocks
    for pre in soup.find_all('pre'):
        pre['class'] = pre.get('class', []) + ['code-block']
    
    # Process inline code
    for code in soup.find_all('code'):
        if code.parent.name != 'pre':
            code['class'] = code.get('class', []) + ['inline-code']
    
    # Process bold and italic text
    for strong in soup.find_all(['strong', 'b']):
        strong['class'] = strong.get('class', []) + ['bold-text']
    
    for em in soup.find_all(['em', 'i']):
        em['class'] = em.get('class', []) + ['italic-text']
    
    # Replace markdown tables with processed HTML tables
    table_tags = soup.find_all('table')
    for i, table_tag in enumerate(table_tags):
        if i < len(processed_tables):
            new_table = BeautifulSoup(processed_tables[i], 'html.parser')
            table_tag.replace_with(new_table)
    
    return str(soup)

def generate_toc(sections):
    toc_html = '<ul>'
    for section in sections:
        toc_html += f'<li><a href="#{section["id"]}"></a></li>'
    toc_html += '</ul>'
    return toc_html

def create_pdf_report(report_title, section_results, end_matter, logo_bytes, primary_color, accent_color):
    with open('code/reports/pdf_report.css', 'r') as file:
        css_template = file.read()
    
    css = css_template.replace("{primary_color}", primary_color).replace("{accent_color}", accent_color)
    
      
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
    for index, (section_name, (section_content, plot_dict, plot_config)) in enumerate(section_results, start=1):
        section_id = section_name.lower().replace(" ", "-")
        html_content = convert_markdown_to_html(section_content, section_name)
        
        # Generate plot image
        plot_image = None
        plot_description = ""
        if plot_dict is not None:
            try:
                plot = go.Figure(data=plot_dict['data'], layout=plot_dict['layout'])
                img_bytes = pio.to_image(plot, format="png", width=600, height=400)
                plot_image = base64.b64encode(img_bytes).decode('utf-8')
                
                plot_description = f"Figure {index}: {plot_config.get('x', 'X')} vs {plot_config.get('y', 'Y')}"
                if plot_config.get('color'):
                    plot_description += f", colored by {plot_config['color']}"
                if plot_config.get('size'):
                    plot_description += f", with size represented by {plot_config['size']}"
                
                plot_description = f'<div class="caption">{plot_description}</div>'
            except Exception as e:
                print(f"Error generating plot: {str(e)}")

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
    
    # Generate PDF
    font_config = FontConfiguration()
    html = HTML(string=html_content)
    css = CSS(string=css)
    
    # Save PDF to a BytesIO object
    pdf_buffer = io.BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=[css], font_config=font_config)
    pdf_buffer.seek(0)

    return pdf_buffer
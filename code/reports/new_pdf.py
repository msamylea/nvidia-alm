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

def convert_markdown_to_html(md_content, section_title):
    # Convert Markdown to HTML with extended features, including TOC
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'sane_lists', 'smarty', 'toc'])
    
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
          
    # Find all tables and add Bootstrap classes
    for table in soup.find_all('table'):
        table['class'] = table.get('class', []) + ['table', 'table-bordered', 'table-striped']
    
    # Ensure each row is split into appropriate columns
    for row in soup.find_all('tr'):
        cells = row.find_all(['th', 'td'])
        for cell in cells:
            cell['style'] = cell.get('style', '') + 'padding: 8px; border: 1px solid #ddd; text-align: left;'
    
    # Process headers and avoid duplicates
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
        
    # Ensure bullet-pointed lists are styled correctly
    for ul in soup.find_all('ul'):
        ul['style'] = ul.get('style', '') + 'list-style-type: disc; margin-left: 10px;'
    
    for ol in soup.find_all('ol'):
        ol['style'] = ol.get('style', '') + 'list-style-type: decimal; margin-left: 10px;'
    
    # Ensure paragraphs are styled correctly
    for p in soup.find_all('p'):
        p['style'] = p.get('style', '') + 'margin-bottom: 10px;'
    
    return str(soup)


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
                    <div class="logo-container">
                        {% if logo %}
                        <img src="data:image/png;base64,{{ logo }}" alt="Logo" class="logo">
                        {% endif %}
                    </div>
                    <h1>{{ report_title }}</h1>
                    <div class="halfline"></div>
                    <p class="date">{{ generated_date }}</p>
                </div>
            </div>
            
            <article id="contents">
                <h2>Table of Contents</h2>
                <ul>
                    {% for section in sections %}
                    <li><a href="#{{ section.id }}">{{ section.title }}</a></li>
                    {% endfor %}
                </ul>
            </article>
            
            <article id="sections">
                {% for section in sections %}
                <div class="section">
                    <h2 id="{{ section.id }}">{{ section.title }}</h2>
                    {{ section.content | safe }}
                    {% if section.plot %}
                    <img src="data:image/png;base64,{{ section.plot }}" alt="Plot" class="plot">
                    {{ section.plot_description | safe }}
                    {% endif %}
                    {% if section.table %}
                    <div class="table-container">
                        {{ section.table | safe }}
                    </div>
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
    for section_name, (section_content, plot_dict, plot_config) in section_results:
        section_id = section_name.lower().replace(" ", "-")
        section_title = section_name
        html_content = convert_markdown_to_html(section_content, section_name)
        
        # Generate plot image
        plot_image = None
        plot_description = ""
        if plot_dict is not None:
            try:
                plot = go.Figure(data=plot_dict['data'], layout=plot_dict['layout'])
                img_bytes = pio.to_image(plot, format="png", width=600, height=400)
                plot_image = base64.b64encode(img_bytes).decode('utf-8')
                
                plot_description = f"Figure: {plot_config.get('x', 'X')} vs {plot_config.get('y', 'Y')}"
                if plot_config.get('color'):
                    plot_description += f", colored by {plot_config['color']}"
                if plot_config.get('size'):
                    plot_description += f", with size represented by {plot_config['size']}"
                
                plot_description = f'<div class="caption">{plot_description}</div>'
            except Exception as e:
                print(f"Error generating plot: {str(e)}")

        processed_sections.append({
            'id': section_id,
            'title': section_name,
            'content': html_content,
            'plot': plot_image,
            'plot_description': plot_description
        })

    end_matter_html = convert_markdown_to_html(end_matter, "End Matter")

    html_content = html_template.render(
        report_title=report_title,
        logo=base64.b64encode(logo_bytes).decode('utf-8') if logo_bytes else None,
        generated_date=datetime.now().strftime('%m-%d-%Y'),
        sections=processed_sections,
        end_matter=end_matter_html
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
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.colors import black, grey
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus.tableofcontents import TableOfContents
from io import BytesIO
import plotly.graph_objects as go
import io
from reportlab.lib import colors
from utils.utilities import extract_content
import markdown
from bs4 import BeautifulSoup

from reportlab.platypus import Paragraph, Spacer

def markdown_to_reportlab(md_text, styles):
    # Convert Markdown to HTML
    html = markdown.markdown(md_text)
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    elements = []
    
    for elem in soup:
        if elem.name is None:  # This is a NavigableString
            continue
        
        text_content = elem.get_text() or ""  # Ensure text content is not None
        if elem.name == 'p':
            elements.append(Paragraph(text_content, styles['Normal']))
            elements.append(Spacer(1, 12))  # Add space after paragraph
        elif elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            style_name = f'Heading{elem.name[1]}'
            elements.append(Paragraph(text_content, styles[style_name]))
            elements.append(Spacer(1, 18))  # Add more space after headings
        elif elem.name == 'ul':
            for li in elem.find_all('li'):
                bullet_text = f"• {li.get_text() or ''}"
                elements.append(Paragraph(bullet_text, styles['BodyText']))
            elements.append(Spacer(1, 12))  # Add space after list
        elif elem.name == 'ol':
            for i, li in enumerate(elem.find_all('li'), 1):
                number_text = f"{i}. {li.get_text() or ''}"
                elements.append(Paragraph(number_text, styles['BodyText']))
            elements.append(Spacer(1, 12))  # Add space after list
        # Add more conditions here for other Markdown elements as needed
    
    return elements

class MyDocTemplate(SimpleDocTemplate):
    def __init__(self, filename, **kw):
        SimpleDocTemplate.__init__(self, filename, **kw)
        self.toc = TableOfContents()
        self.toc.levelStyles = [
            ParagraphStyle(fontName='Helvetica-Bold', fontSize=14, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=16),
            ParagraphStyle(fontName='Helvetica', fontSize=12, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=3, leading=14),
            ParagraphStyle(fontName='Helvetica', fontSize=10, name='TOCHeading3', leftIndent=60, firstLineIndent=-20, spaceBefore=2, leading=12),
        ]

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                self.toc.addEntry(0, text, self.page)
            elif style == 'Heading2':
                self.toc.addEntry(1, text, self.page)
            elif style == 'Heading3':
                self.toc.addEntry(2, text, self.page)

def create_pdf_report(report_title, section_results, end_matter, output_buffer):
    doc = MyDocTemplate(output_buffer, pagesize=letter, 
                        rightMargin=72, leftMargin=72,
                        topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='CustomBodyText', parent=styles['Normal'], leading=12, bulletIndent=4, spaceBefore=6, spaceAfter=6, bulletAnchor='start'))
    styles.add(ParagraphStyle(name='CustomTitlePage', parent=styles['Title'], alignment=TA_CENTER, spaceBefore=36))

    # Create the story (content) for the PDF
    story = []

    # Add title page
    story.append(Paragraph(report_title, styles['CustomTitlePage']))
    story.append(PageBreak())

    # Add Table of Contents placeholder
    toc_placeholder = Paragraph("Table of Contents", styles['Heading1'])
    story.append(toc_placeholder)
    story.append(doc.toc)
    story.append(PageBreak())

    # Add sections
    for section_name, (section_content, plot_dict, plot_config) in section_results:
        # Add section header
        story.append(Paragraph(section_name, styles['Heading2']))
        story.append(Spacer(1, 12))

        # Add section content
        elements = extract_content(section_content)
        last_heading = None
        for element_type, element in elements:
            if element_type == 'text':
                parsed_elements = markdown_to_reportlab(element, styles)
                for parsed_element in parsed_elements:
                    if isinstance(parsed_element, Paragraph):
                        # Check for duplicate headings
                        if parsed_element.style.name.startswith('Heading') and parsed_element.text == last_heading:
                            continue
                        last_heading = parsed_element.text
                    story.append(parsed_element)
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
                
                table = Table(table_data, spaceAfter=6)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('TEXTCOLOR', (0, 1), (-1, -1), black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, black)
                ]))
                story.append(table)
                story.append(Spacer(1, 12))

        # Add plot if available
        if plot_dict is not None:
            # Convert Plotly figure to static image
            plot = go.Figure(data=plot_dict['data'], layout=plot_dict['layout'])
            img_buffer = io.BytesIO()
            plot.write_image(img_buffer, format="png", width=600, height=400)
            img_buffer.seek(0)
            img = Image(img_buffer)
            img.drawHeight = 4*inch
            img.drawWidth = 8*inch
            story.append(img)
            story.append(Spacer(1, 12))

            # Add plot description
            plot_description = f"<b><center>Figure: {plot_config.get('x', 'X')} vs {plot_config.get('y', 'Y')}"
            if plot_config.get('color'):
                plot_description += f", colored by {plot_config['color']}"
            if plot_config.get('size'):
                plot_description += f", with size representing {plot_config['size']}"
            plot_description += "</center></b>"
            story.append(Paragraph(plot_description, styles['Italic']))
            story.append(Spacer(1, 12))

        # Add a page break after each section
        story.append(PageBreak())

    story.append(Paragraph("Conclusion and Recommendations", styles['Heading2']))
    story.append(Spacer(1, 12))
    end_elements = extract_content(end_matter)
    last_heading = None
    for element_type, element in end_elements:
        if element_type == 'text':
            parsed_elements = markdown_to_reportlab(element, styles)
            for parsed_element in parsed_elements:
                if isinstance(parsed_element, Paragraph):
                    # Check for duplicate headings
                    if parsed_element.style.name.startswith('Heading') and parsed_element.text == last_heading:
                        continue
                    last_heading = parsed_element.text
                story.append(parsed_element)
            story.append(Spacer(1, 6))

    # Build the PDF
    doc.multiBuild(story)
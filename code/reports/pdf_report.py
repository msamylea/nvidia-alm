from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, FrameBreak, KeepTogether, ActionFlowable
from reportlab.lib.colors import black, grey, white
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus.tableofcontents import TableOfContents
from datetime import datetime
from reportlab.platypus import HRFlowable
import plotly.graph_objects as go
import io
from reportlab.lib import colors
from utils.utilities import extract_content
import markdown
from bs4 import BeautifulSoup
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

def markdown_to_reportlab(md_text, styles):
    html = markdown.markdown(md_text)
    soup = BeautifulSoup(html, 'html.parser')
    elements = []
    
    for elem in soup:
        if elem.name is None:
            continue
        
        text_content = elem.get_text() or ""
        if elem.name == 'p':
            elements.append(Paragraph(text_content, styles['Normal']))
            elements.append(Spacer(1, 12))
        elif elem.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
            style_name = f'Heading{elem.name[1]}'
            elements.append(Paragraph(text_content, styles[style_name]))
            elements.append(Spacer(1, 18))
        elif elem.name == 'ul':
            for li in elem.find_all('li'):
                bullet_text = f"• {li.get_text() or ''}"
                elements.append(Paragraph(bullet_text, styles['CustomBodyText']))
            elements.append(Spacer(1, 12))
        elif elem.name == 'ol':
            for i, li in enumerate(elem.find_all('li'), 1):
                number_text = f"{i}. {li.get_text() or ''}"
                elements.append(Paragraph(number_text, styles['CustomBodyText']))
            elements.append(Spacer(1, 12))
    
    return elements

class MyDocTemplate(SimpleDocTemplate):
    def __init__(self, filename, report_title, logo, primary_color, secondary_color, accent_color, **kw):
        SimpleDocTemplate.__init__(self, filename, **kw)
        self.report_title = report_title
        self.logo = logo
        self.primary_color = HexColor(f"#{primary_color}")
        self.secondary_color = HexColor(f"#{secondary_color}")
        self.accent_color = HexColor(f"#{accent_color}")
        self.toc = TableOfContents()
        self.toc.levelStyles = [
            ParagraphStyle(fontName='Helvetica-Bold', fontSize=14, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=16),
            ParagraphStyle(fontName='Helvetica', fontSize=12, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=3, leading=14),
            ParagraphStyle(fontName='Helvetica', fontSize=10, name='TOCHeading3', leftIndent=60, firstLineIndent=-20, spaceBefore=2, leading=12),
        ]
        self.width = letter
        self.height = letter
        
        self.styles = getSampleStyleSheet()
        self.styles['Title'].alignment = TA_CENTER
        self.styles['Title'].spaceAfter = 36

        self.styles['Heading1'].fontSize = 24
        self.styles['Heading1'].textColor = self.primary_color
        self.styles['Heading1'].spaceAfter = 12

        self.styles['Normal'].fontSize = 10
        self.styles['Normal'].leading = 14
        self.styles['Normal'].textColor = HexColor('#202124')

        self.styles.add(ParagraphStyle(name='Center', parent=self.styles['Normal'], alignment=TA_CENTER))
        self.styles.add(ParagraphStyle(name='CustomBodyText', parent=self.styles['Normal'], leading=12, bulletIndent=4, spaceBefore=6, spaceAfter=6, bulletAnchor='start'))
        self.styles.add(ParagraphStyle(name='Caption', parent=self.styles['Normal'], fontSize=10, textColor=self.primary_color, alignment=TA_CENTER))

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

    def afterPage(self):
        canvas = self.canv
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(inch, 10.5*inch, "Your Company Name")
        canvas.drawString(inch, 0.75*inch, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()
        
    def beforeDocument(self):
        self.handle_coverPage()
        self.handle_pageBreak()
    
    def handle_coverPage(self):
        self.canv.saveState()
        letter_width, letter_height = letter
        
        # Set the background to white
        self.canv.setFillColor(white)
        self.canv.rect(0, 0, letter_width, letter_height, fill=1)
        
        # Set the text color to primary color
        self.canv.setFillColor(self.primary_color)
        self.canv.setFont('Helvetica-Bold', 24)
        
        # Set the logo size to be half the width of the page
        logo_width = letter_width / 2
        logo_height = logo_width / 2  # Adjust this to preserve aspect ratio if needed
        
        # Calculate positions
        title_y_position = letter_height / 2 + 50
        logo_y_position = title_y_position + 1 * inch  # 1 inch above the title
        
        if self.logo:
            try:
                self.canv.drawImage(ImageReader(io.BytesIO(self.logo)),
                                    letter_width / 2 - logo_width / 2,
                                    logo_y_position,
                                    width=logo_width,
                                    height=logo_height,
                                    preserveAspectRatio=True)
            except Exception as e:
                print(f"Warning: Unable to load logo: {e}")
        
        # Draw the title and date
        self.canv.drawCentredString(letter_width / 2, title_y_position, self.report_title)
        self.canv.drawCentredString(letter_width / 2, title_y_position - 80, 
                                    f"Generated on: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Draw a thick line spaced under the title and date
        self.canv.setLineWidth(2)
        self.canv.setStrokeColor(self.primary_color)
        self.canv.line(letter_width / 4, title_y_position - 100, 3 * letter_width / 4, title_y_position - 100)
        
        self.canv.restoreState()
        
    def handle_pageBreak(self):
        self.canv.showPage()

def create_section_page(doc, section_name):
    centered_heading_style = doc.styles['Heading1'].clone('CenteredHeading1')
    centered_heading_style.alignment = TA_CENTER
    if 'SectionPageHeading' not in doc.styles:
        section_style = doc.styles.add(ParagraphStyle(name="SectionPageHeading", parent=centered_heading_style, textColor=doc.secondary_color))
    else:
        section_style = doc.styles['SectionPageHeading']

    section_page = []
    page_height = letter[1]  # Get the height of the page
    title_height = 24  # Approximate height of the title (adjust as needed)
    
    # Calculate the vertical space needed to center the title
    vertical_space = (page_height - title_height) / 2
    
    section_page.append(FrameBreak())
    section_page.append(Spacer(1, vertical_space - 36))  # Adjust for better centering
    section_page.append(Paragraph(section_name, section_style))
    section_page.append(Spacer(1, vertical_space))
    section_page.append(FrameBreak())
    return section_page

def safe_keep_together(elements):
    if any(isinstance(e, ActionFlowable) for e in elements):
        return elements
    return [KeepTogether(elements)] if elements else []

def create_pdf_report(report_title, section_results, end_matter, output_buffer, logo, primary_color, secondary_color, accent_color):
    doc = MyDocTemplate(output_buffer, report_title, logo, primary_color, secondary_color, accent_color, pagesize=letter, 
                        rightMargin=72, leftMargin=72,
                        topMargin=72, bottomMargin=72)

    create_section_page(doc, "Initialize Styles")

    story = []

    # Add Table of Contents
    story.append(Paragraph("Table of Contents", doc.styles['Heading1']))
    story.append(Spacer(1, 12))
    story.append(doc.toc)
    story.append(PageBreak())

    for section_name, (section_content, plot_dict, plot_config) in section_results:
        section_story = []
        section_title_page = create_section_page(doc, section_name)
        section_story.extend(section_title_page)

        elements = extract_content(section_content)
        for element_type, element in elements:
            if element_type == 'text':
                parsed_elements = markdown_to_reportlab(element, doc.styles)
                section_story.extend(parsed_elements)
            elif element_type == 'table':
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
                else:
                    continue
                
                table = create_table(table_data, doc.accent_color)
                section_story.append(table)
                section_story.append(Spacer(1, 12))

        if plot_dict is not None:
            try:
                plot = go.Figure(data=plot_dict['data'], layout=plot_dict['layout'])
                img_buffer = io.BytesIO()
                plot.write_image(img_buffer, format="png", width=600, height=400)
                img_buffer.seek(0)
                img = Image(img_buffer)
                img.drawHeight = 4*inch
                img.drawWidth = 6*inch
                section_story.append(img)
                section_story.append(Spacer(1, 12))

                plot_description = f"Figure: {plot_config.get('x', 'X')} vs {plot_config.get('y', 'Y')}"
                if plot_config.get('color'):
                    plot_description += f", colored by {plot_config['color']}"
                if plot_config.get('size'):
                    plot_description += f", with size representing {plot_config['size']}"
                section_story.append(Paragraph(plot_description, doc.styles['Caption']))
                section_story.append(Spacer(1, 12))
            except Exception as e:
                print(f"Error generating plot: {e}")
                section_story.append(Paragraph("Error: Unable to generate plot", doc.styles['Normal']))

        story.extend(safe_keep_together(section_story))
        story.append(PageBreak())

    # Conclusion and Recommendations
    conclusion_story = []
    conclusion_story.append(Paragraph("Conclusion and Recommendations", doc.styles['Heading2']))
    conclusion_story.append(Spacer(1, 12))
    end_elements = extract_content(end_matter)
    for element_type, element in end_elements:
        if element_type == 'text':
            parsed_elements = markdown_to_reportlab(element, doc.styles)
            conclusion_story.extend(parsed_elements)
    
    story.extend(safe_keep_together(conclusion_story))

    # Build the PDF
    doc.multiBuild(story)
    
def create_table(data, accent_color, colWidths=None):
    available_width = letter[0] - 2*72  # letter[0] is page width, 72 points = 1 inch margin on each side
    
    if colWidths is None:
        # Distribute width evenly among columns
        colWidths = [available_width/len(data[0])] * len(data[0])
    
    table = Table(data, colWidths=colWidths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), accent_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
    ]))
    return KeepTogether(table)

def add_section_separator(story, primary_color):
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color))
    story.append(Spacer(1, 12))

def add_image_with_caption(story, image_path, caption, styles):
    try:
        img = Image(image_path, width=6*inch, height=4*inch)
        story.append(img)
        story.append(Spacer(1, 6))
        story.append(Paragraph(caption, styles['Caption']))
        story.append(Spacer(1, 12))
    except Exception as e:
        print(f"Warning: Unable to load image from {image_path}: {e}")
        story.append(Paragraph(f"Image not available: {caption}", styles['Normal']))
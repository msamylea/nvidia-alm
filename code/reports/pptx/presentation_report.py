from pptx import Presentation
from io import BytesIO
import sys
import os
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.configs import get_llm
from prompts.presentation_prompt_template import presentation_prompt
import random
import re

def select_slide_layout(slide_content, include_plot, include_table):
    if include_plot and include_table:
        include_table = False 
    if 'section_title' in slide_content and 'content' in slide_content:
        if include_table:
            return 4  
        elif include_plot:
            layout_choice = random.choice([2, 3])  
            return layout_choice
        else:
            return 1  
    elif 'report_title' in slide_content:
        return 0  
    else:
        return 1  

def get_presentation_content(content):
    if isinstance(content, dict):
        content = {k: v for k, v in content.items() if k != 'plot_image'}
        content = str(content)
    prompt = presentation_prompt.replace("{section_content}", content)
    llm = get_llm()
    response = llm.get_response(prompt)
    return response


def parse_slides(section_content):
    if isinstance(section_content, dict):
        content = section_content.get("content", "")
    else:
        content = section_content
    
    if isinstance(content, list):
        content = "\n".join(content)  # Convert list to string
    
    response = get_presentation_content(content)
    slides = []
    
    slide_pattern = re.compile(r'<Slide>(.*?)</Slide>', re.DOTALL)
    for slide_match in slide_pattern.finditer(response):
        slide_content = slide_match.group(1)
        
        report_title_match = re.search(r'<Report_Title>(.*?)</Report_Title>', slide_content, re.DOTALL)
        report_title = report_title_match.group(1) if report_title_match else None
        
        title_match = re.search(r'<Section_Title>(.*?)</Section_Title>', slide_content, re.DOTALL)
        section_title = title_match.group(1) if title_match else report_title
        
        content_match = re.search(r'<Content>(.*?)</Content>', slide_content, re.DOTALL)
        content = []
        if content_match:
            for line in content_match.group(1).strip().split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    content.append({'type': 'bullet', 'text': line[2:].strip()})
                else:
                    content.append({'type': 'paragraph', 'text': line})
        
        table_match = re.search(r'<Table>(.*?)</Table>', slide_content, re.DOTALL)
        table = None
        if table_match:
            table_text = table_match.group(1).strip()
            table = parse_markdown_table(table_text)
        
        slide_data = {
            'report_title': report_title,
            'section_title': section_title,
            'content': content,
            'table': table,
        }
        
       
        slides.append(slide_data)
    
    return slides


def parse_markdown_table(markdown_table):
    try:
        lines = markdown_table.strip().split('\n')
        if len(lines) < 3:  
            return None

        headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
        data = []
        for line in lines[2:]:  # Skip the separator line
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                data.append(cells)
        
        if not data:
            return None
        
        if headers and data:
            return {'headers': headers, 'data': data}
        else:
            return None
    except Exception as e:
        return None
    
def create_presentation(section_content, prs=None, selected_template='default'):
    if prs is None:
        if selected_template == 'default':
            prs = Presentation('code/templates/BlueYellow.pptx')
        else:
            prs = Presentation(f"code/templates/{selected_template}.pptx")
        
    if not prs.slides:
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])
        report_title = title_slide.shapes.title
        report_title.text = section_content.get('report_title', 'Untitled Presentation')
    
    slides = parse_slides(section_content)
    plot_image = section_content.get('plot_image')
    
    for index, slide_content in enumerate(slides):
        slide_number = len(prs.slides) + 1
        include_plot = plot_image is not None
        include_table = slide_content.get('table') is not None
        
        layout_index = select_slide_layout(slide_content, include_plot=include_plot, include_table=include_table)
        slide = prs.slides.add_slide(prs.slide_layouts[layout_index])
        
        # Ensure the section title is always set
        section_title = slide_content.get('section_title', 'Untitled Section')
        if section_title == 'Untitled Section' and 'report_title' in slide_content:
            section_title = slide_content['report_title']
        
        # Debug print to check the section title
        print(f"Slide {slide_number} section title: {section_title}")
        
        # Ensure the title placeholder is found and set
        title_placeholder = slide.shapes.title
        if title_placeholder:
            title_placeholder.text = section_title
            print(f"Slide {slide_number} title set to: {section_title}")
        else:
            print(f"Slide {slide_number} has no title placeholder")
        
        add_content_to_slide(slide, slide_content)
        
        if include_table:
            add_table_to_slide(slide, slide_content['table'])
        
        if include_plot:
            add_plot_to_slide(slide, plot_image)
            plot_image = None

    return prs

def add_plot_to_slide(slide, plot_image):
    if not plot_image:
        return None

    try:
        plot_placeholder = find_plot_placeholder(slide)
        img_bytes = base64.b64decode(plot_image)
        plot_placeholder.insert_picture(BytesIO(img_bytes))
    except Exception as e:
        return None
        
def add_content_to_slide(slide, slide_content):
    content_placeholder = find_content_placeholder(slide)
    text_frame = content_placeholder.text_frame
    text_frame.clear()  # Clear any existing content

    for item in slide_content['content']:
        if item['type'] == 'paragraph':
            p = text_frame.add_paragraph()
            p.text = item['text']
            p.level = 0
        elif item['type'] == 'bullet':
            p = text_frame.add_paragraph()
            p.text = item['text']
            p.level = 1

def add_plot_to_slide(slide, plot_image):
    if not plot_image:
        return None

    try:
        plot_placeholder = find_plot_placeholder(slide)
        
        img_bytes = base64.b64decode(plot_image)
        plot_placeholder.insert_picture(BytesIO(img_bytes))
    except Exception as e:
        return None
    
def find_content_placeholder(slide):
    for placeholder in slide.placeholders:
        if placeholder.placeholder_format.idx != 0:  # Skip title placeholder
            return placeholder
    return None

def find_plot_placeholder(slide):
    for shape in slide.placeholders:
        if shape.placeholder_format.type in [18, 13, 7]:  
            return shape
    return None

def find_table_placeholder(slide):
    for shape in slide.placeholders:
        if shape.placeholder_format.type == 12:  # Table placeholder
            return shape
    return None

def add_table_to_slide(slide, table_data):
    if table_data is None or 'headers' not in table_data or 'data' not in table_data:
        return
    try:
        table_placeholder = find_table_placeholder(slide)
        rows = len(table_data['data']) + 1  # +1 for header
        cols = len(table_data['headers'])
        
        table = table_placeholder.insert_table(rows, cols).table
        for col_idx, header in enumerate(table_data['headers']):
            table.cell(0, col_idx).text = header
        
        for row_idx, row in enumerate(table_data['data']):
            for col_idx, cell in enumerate(row):
                table.cell(row_idx + 1, col_idx).text = cell
    except Exception as e:
        return None
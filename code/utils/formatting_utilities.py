import re
import dash_ag_grid as dag
from markdown import markdown
from bs4 import BeautifulSoup
from typing import Any, Dict
from dash import html


def format_markdown_content(content):
    lines = content.split('\n')
    formatted_content = []
    current_list = None
    h2_texts = set()  # Keep track of h2 texts
    
    for line in lines:
        if line.startswith("Error"):
            continue
        if line.startswith('# '):
            h2_text = line[2:]
            formatted_content.append(html.H2(h2_text))
            h2_texts.add(h2_text)
        elif line.startswith('## '):
            h3_text = line[3:]
            if h3_text not in h2_texts:  # Only add h3 if its text is not in h2_texts
                formatted_content.append(html.H3(h3_text))
        elif line.startswith('### '):
            h4_text = line[4:]
            if h4_text not in h2_texts:  # Only add h4 if its text is not in h2_texts
                formatted_content.append(html.H4(h4_text))
        elif line.startswith('#### '):
            formatted_content.append(html.H5(line[5:]))
        elif line.startswith('- ') or line.startswith('* '):
            if current_list is None:
                current_list = html.Ul()
            current_list.children.append(html.Li(line[2:]))
        elif line.strip() == '':
            if current_list is not None:
                formatted_content.append(current_list)
                current_list = None
            formatted_content.append(html.Br())
        else:
            if current_list is not None:
                formatted_content.append(current_list)
                current_list = None
            formatted_content.append(html.P(line))
    
    if current_list is not None:
        formatted_content.append(current_list)
    
    return formatted_content

def remove_duplicate_lines(text):
    seen = set()
    result = []
    for line in text.split('\n'):
        if line not in seen:
            seen.add(line)
            result.append(line)
    return '\n'.join(result)

def post_process_markdown(content):
    # Convert to HTML and back to markdown for consistent formatting
    html = markdown(content)
    soup = BeautifulSoup(html, 'html.parser')

    # Standardize headers
    for i in range(1, 7):
        for header in soup.find_all(f'h{i}'):
            header.name = f'h{i}'

    # Standardize lists
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            li.string = f"* {li.get_text().strip()}"

    for ol in soup.find_all('ol'):
        for i, li in enumerate(ol.find_all('li'), start=1):
            li.string = f"{i}. {li.get_text().strip()}"

    # Convert back to markdown
    processed_content = soup.get_text()

    # Additional formatting (e.g., for code blocks, tables)
    processed_content = re.sub(r'```(\w+)\n', r'```\1\n', processed_content)
    processed_content = re.sub(r'\n\n\|', r'\n\n| ', processed_content)

    return processed_content

def generate_plot_title(plot_config: Dict[str, Any]) -> str:
    """Generate a descriptive title for the plot based on its configuration."""
    x = plot_config.get('x', 'X')
    y = plot_config.get('y', 'Y')
    plot_type = plot_config.get('type', 'scatter')
    title = f"{plot_type.capitalize()} Plot: {y} vs {x}"
    
    if plot_config.get('color'):
        title += f", colored by {plot_config['color']}"
    if plot_config.get('size'):
        title += f", size representing {plot_config['size']}"
    
    return title

def parse_markdown_table(markdown_table):
    lines = markdown_table.strip().split('\n')
    headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
    data = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        if cells:
            data.append(cells)
    return {'headers': headers, 'data': data}

def preprocess_text(text):
    # Zero-width space character
    zws = '\u200B'
    
    # Insert zero-width space after opening square bracket and before closing square bracket
    text = re.sub(r'\[', f'[{zws}', text)
    text = re.sub(r'\]', f'{zws}]', text)
    
    # Insert zero-width space before and after equals sign
    text = re.sub(r'=', f'{zws}={zws}', text)
    
    # Insert zero-width space before and after approximate equals sign
    text = re.sub(r'≈', f'{zws}≈{zws}', text)
    
    # Insert zero-width space after dollar sign
    text = re.sub(r'\$', f'${zws}', text)
    
    # Insert zero-width space before percent sign
    text = re.sub(r'%', f'{zws}%', text)
    
    # Insert zero-width space after 'r' and before 'p-value' in correlation statistics
    text = re.sub(r'(r\s*≈)', lambda m: f'{m.group(1)}{zws}', text)
    text = re.sub(r'(p-value)', f'{zws}p-value', text)
    
    text = re.sub(r'(=​)+', '', text)
        
    text = remove_duplicate_lines(text)
    
    return text

def create_ag_grid(table_str):
    rows = [row.strip() for row in table_str.split('\n') if row.strip()]
    headers = [cell.strip() for cell in rows[0].split('|') if cell.strip()]
    data = []
    for row in rows[2:]:  # Skip the header separator row
        cells = [cell.strip() for cell in row.split('|') if cell.strip()]
        if len(cells) == len(headers):
            data.append(dict(zip(headers, cells)))
    
    column_defs = [{"field": h} for h in headers]
    
    return dag.AgGrid(
        columnDefs=column_defs,
        rowData=data,
        dashGridOptions={"pagination": True, "paginationAutoPageSize": True},
        style={"height": "300px", "width": "100%"},
        columnSize='sizeToFit',
        className='ag-theme-alpine-dark'
    )


def reduce_figure_size(fig):
    # Remove unnecessary attributes
    for trace in fig['data']:
        trace.pop('hovertemplate', None)
        trace.pop('hoverlabel', None)
    
    # Simplify layout
    fig['layout'].pop('scene', None)
    fig['layout'].pop('xaxis', None)
    fig['layout'].pop('yaxis', None)
    
    return fig

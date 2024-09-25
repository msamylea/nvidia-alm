from typing import Any, Dict

def remove_duplicate_lines(text):
    seen = set()
    result = []
    for line in text.split('\n'):
        if line not in seen:
            seen.add(line)
            result.append(line)
    return '\n'.join(result)


def generate_plot_title(plot_config: Dict[str, Any]) -> str:
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


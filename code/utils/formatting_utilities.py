from typing import Any, Dict

def remove_duplicate_lines(text):
    """
    Remove duplicate lines from a given text.

    Args:
        text (str): The input text containing multiple lines.

    Returns:
        str: A string with duplicate lines removed, preserving the order of first occurrences.
    """
    seen = set()
    result = []
    for line in text.split('\n'):
        if line not in seen:
            seen.add(line)
            result.append(line)
    return '\n'.join(result)


def generate_plot_title(plot_config: Dict[str, Any]) -> str:
    """
    Generates a plot title based on the provided plot configuration.
    Args:
        plot_config (Dict[str, Any]): A dictionary containing plot configuration.
            Expected keys:
                - 'x' (str): Label for the x-axis. Default is 'X'.
                - 'y' (str): Label for the y-axis. Default is 'Y'.
                - 'type' (str): Type of the plot (e.g., 'scatter', 'line'). Default is 'scatter'.
                - 'color' (str, optional): Label for the color dimension.
                - 'size' (str, optional): Label for the size dimension.
    Returns:
        str: The generated plot title.
    """
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
    """
    Parses a markdown table and returns its headers and data.

    Args:
        markdown_table (str): A string representation of a markdown table.

    Returns:
        dict: A dictionary with two keys:
            - 'headers': A list of header names.
            - 'data': A list of rows, where each row is a list of cell values.
    """
    lines = markdown_table.strip().split('\n')
    headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
    data = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        if cells:
            data.append(cells)
    return {'headers': headers, 'data': data}


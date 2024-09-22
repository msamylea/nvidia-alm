import asyncio
from typing import Any, Dict, List, Tuple
from .create_sections import get_outline, summarize_section_async, write_section_async, write_recommendations_conclusions_async
from utils.utilities import generate_plot_title, extract_table_from_content
from plots.plot_factory import parse_llm_response
from utils.cache_config import cache, cache_key
import sys

def log_info(message):
    print(f"INFO: {message}", flush=True)
    sys.stdout.flush()

def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr, flush=True)
    sys.stderr.flush()



async def create_final_report(query: str, max_samples: int = 10000) -> Tuple[str, List[Tuple[str, Tuple[str, Any, Any]]], str, Dict[str, Any]]:
    report_key = cache_key(query, max_samples)
    cached_report = cache.get(report_key)
    if cached_report is not None:
        return cached_report

    report_title, section_names, num_sections = await get_outline(query)
    
    section_tasks = [
        write_section_async(section_name, query)
        for section_name in section_names
    ]

    section_results = await asyncio.gather(*section_tasks)
    
    summarized_sections = []
    for i, (section_name, section_content) in enumerate(section_results):
        plot, plot_data, plot_config = await parse_llm_response(section_name, max_samples=max_samples)
       
        summary = await summarize_section_async(section_content)
        summarized_sections.append((section_name, summary))
        
        section_results[i] = (section_name, (section_content, plot, plot_config))
    
    end_matter = await write_recommendations_conclusions_async(summarized_sections)
    
    presentation_content = {
        "report_title": report_title,
        "section_title": section_names[-1] if section_names else "",
        "slides": []
    }

    for section_name, (section_content, plot, plot_config) in section_results:
        # Add content slide
        presentation_content["slides"].append({
            "report_title": report_title,
            "section_title": section_name,
            "content": section_content,
            "table": extract_table_from_content(section_content)
        })

        # Add plot slide if plot exists
        if plot and plot_config:
            plot_title = generate_plot_title(plot_config)
            presentation_content["slides"].append({
                "title": plot_title,
                "plot": plot,
                "is_plot_slide": True
            })

    result = (report_title, section_results, end_matter, presentation_content)
    cache.set(report_key, result, timeout=3600)
    return result




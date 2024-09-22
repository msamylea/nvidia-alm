
from prompts.report_prompt_template import prepare_outline_prompt, summarize_prompt, write_section_prompt, write_recommendations_conclusions_prompt
from utils.cache_config import cache, cache_key
import json
from utils.utilities import parse_and_correct_json
from .llm_report_handling import get_outline_response, get_llm_response
from .data_router import get_schema, get_summary

async def get_outline(query: str):
    outline_key = cache_key(query)
    cached_result = cache.get(outline_key)
    if cached_result is not None:
        return cached_result

    try:
        schema = get_schema()
        summary = get_summary()

        columns = schema.get('columns', [])
        columns_str = ', '.join(columns)
        summary_str = json.dumps(summary, indent=2)

        context = f"""
        Columns:
        {columns_str}

        Summary:
        {summary_str}

        Query:
        {query}
        """

        prompt = prepare_outline_prompt.replace("{dataset_context}", context)
        response = await get_outline_response(prompt)
        outline = parse_and_correct_json(response)

        report_title = outline['Report_Title']
        section_names = [section['Section_Name'] for section in outline['Sections']]
        num_sections = len(section_names)

        result = (report_title, section_names, num_sections)

        cache.set(outline_key, result, timeout=300)
        return result
    except Exception as e:
        return "Error Report", ["Error Section"], 1

async def summarize_section_async(section_result: str):
    prompt = summarize_prompt.replace("{section_content}", section_result)
    response = await get_llm_response(prompt)
    return response

async def write_section_async(section_name: str, query: str):
    schema = get_schema()
    summary = get_summary()

    schema_str = json.dumps(schema, indent=2)
    summary_str = json.dumps(summary, indent=2)

    prompt = write_section_prompt.replace("{section_name}", section_name).replace("{user_query}", query).replace("{schema}", schema_str).replace("{summary}", summary_str)
    try:
        response = await get_llm_response(prompt, section_name)
        return (section_name, response.strip())
    except Exception as e:
        return (section_name, f"Error generating content for this section: {str(e)}")

async def write_recommendations_conclusions_async(section_results):
    combined_sections = "\n\n".join([f"{name}\n{content}" for name, content in section_results])

    prompt = write_recommendations_conclusions_prompt.replace("{combined_sections}", combined_sections)

    response = await get_llm_response(prompt, "Recommendations and Conclusions")
    return response
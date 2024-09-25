
from prompts.report_prompt_template import prepare_outline_prompt, summarize_prompt, write_section_prompt, write_recommendations_conclusions_prompt
from utils.cache_config import cache, cache_key
import json
from utils.utilities import parse_and_correct_json
from .llm_report_handling import get_outline_response, get_llm_response_for_section
from utils.data_cache import cached_get_summary, cached_get_schema


async def get_outline(query: str):
    """
    Generates an outline for a report based on the provided query.

    This function attempts to retrieve a cached outline for the given query.
    If no cached result is found, it generates a new outline by fetching the
    schema and summary, preparing the context, and making an asynchronous
    request to get the outline response. The result is then cached for future
    use.

    Args:
        query (str): The query string for which the outline is to be generated.

    Returns:
        tuple: A tuple containing the report title (str), a list of section names (list of str),
               and the number of sections (int). In case of an error, returns a default error
               report with a single error section.
    """
    
    outline_key = cache_key(query)
    cached_result = cache.get(outline_key)
    if cached_result is not None:
        return cached_result

    try:
        schema = cached_get_schema()
        summary = cached_get_summary()

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
    """
    Asynchronously summarizes a given section of text using a language model.

    Args:
        section_result (str): The content of the section to be summarized.

    Returns:
        str: The summarized text of the section.
    """
    prompt = summarize_prompt.replace("{section_content}", section_result)
    response = await get_llm_response_for_section(prompt)
    return response

async def write_section_async(section_name: str, query: str):
    """
    Asynchronously generates content for a given section using a language model.

    Args:
        section_name (str): The name of the section to generate content for.
        query (str): The user query to be included in the prompt.

    Returns:
        tuple: A tuple containing the section name and the generated content or an error message.

    Raises:
        Exception: If there is an error generating content for the section.
    """
    schema = cached_get_schema()
    summary = cached_get_summary()

    schema_str = json.dumps(schema, indent=2)
    summary_str = json.dumps(summary, indent=2)

    prompt = write_section_prompt.replace("{section_name}", section_name).replace("{user_query}", query).replace("{schema}", schema_str).replace("{summary}", summary_str)
    try:
        response = await get_llm_response_for_section(prompt, section_name)
        return (section_name, response.strip())
    except Exception as e:
        return (section_name, f"Error generating content for this section: {str(e)}")

async def write_recommendations_conclusions_async(section_results):
    """
    Asynchronously generates the "Recommendations and Conclusions" section based on provided section results.

    Args:
        section_results (list of tuples): A list of tuples where each tuple contains a section name and its content.

    Returns:
        str: The generated "Recommendations and Conclusions" section as a string.

    Raises:
        Exception: If there is an issue with generating the response from the language model.
    """
    combined_sections = "\n\n".join([f"{name}\n{content}" for name, content in section_results])

    prompt = write_recommendations_conclusions_prompt.replace("{combined_sections}", combined_sections)

    response = await get_llm_response_for_section(prompt, "Recommendations and Conclusions")
    return response
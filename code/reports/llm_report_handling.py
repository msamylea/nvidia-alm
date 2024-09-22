import re
import asyncio
from utils.configs import llm
from .data_router import get_schema, get_sample, get_column_stats, get_value_counts, sum_single_column, detect_outliers, get_summary


async def get_outline_response(prompt):
    print("CALLED LLM FOR OUTLINE")
    context = f"""
    Using the provided context, generate an outline for a report based on the dataset.
    
    Context: {prompt}
    """
    
    response = await asyncio.to_thread(llm.get_response, context)
    
    return response

async def get_llm_response(prompt: str, section_name: str = None) -> str:
    print("CALLED LLM FOR REPORT SECTION")
    schema = get_schema()
    columns = list(schema.keys())
    
    context = f"""
    You are an AI assistant analyzing a dataset.

    You can use these functions to get data:
    
    1. get_schema(): Get detailed dataset schema
    2. get_summary(): Get summary statistics
    3. get_sample(n=5): Get n sample rows
    4. get_column_stats(column_name): Get stats for a specific column
    5. get_value_counts(column_name): Get top value counts for a specific column
    6. sum_single_column(column_name): Get the sum of a single column
    7. detect_outliers(column_name): Detect outliers in a column

    IMPORTANT: Only use column names that exist in the dataset. 
    If you're not sure if a column exists, use the get_schema() function to check.

    To use a function, write it exactly as shown above, replacing parameters as needed.
    For example, to get a sample of 10 rows, write: get_sample(10)

    Analyze the data based on this prompt: {prompt}

    If you cannot answer the prompt using the available data, say so explicitly.
    DO NOT make up or assume any information that is not provided by these functions.
    """
    try:
        response = await asyncio.to_thread(llm.get_response, context)
    except Exception as e:
        return f"Error: {str(e)}"

    function_calls = re.findall(r'(get_\w+\([^)]*\))', response)
    
    for full_call in function_calls:
        try:
            if full_call.startswith("get_sample("):
                match = re.search(r'get_sample\((\d*)\)', full_call)
                n = int(match.group(1)) if match and match.group(1) else 5
                result = get_sample(n)
            elif full_call.startswith("get_column_stats("):
                column_name = re.search(r'get_column_stats\((.*?)\)', full_call).group(1).strip("'\"")
                result = get_column_stats(column_name)
            elif full_call.startswith("get_value_counts("):
                match = re.search(r'get_value_counts\((.*?)\)', full_call)
                params = match.group(1).split(',')
                column_name = params[0].strip("'\"")
                top_n = int(params[1].split('=')[1]) if len(params) > 1 else 10
                result = get_value_counts(column_name)
            elif full_call == "get_schema()":
                result = get_schema()
            elif full_call.startswith("sum_single_column("):
                column_name = re.search(r'sum_single_column\((.*?)\)', full_call).group(1).strip("'\"")
                result = sum_single_column(column_name)
            elif full_call == "get_summary()":
                result = get_summary()
            elif full_call.startswith("detect_outliers("):
                column_name = re.search(r'detect_outliers\((.*?)\)', full_call).group(1).strip("'\"")
                result = detect_outliers(column_name)
            else:
                result = f"Error: Unknown function call '{full_call}'"
        except Exception as e:
            result = f"Error executing {full_call}: {str(e)}"

        response = response.replace(full_call, str(result))

    # Reprocess the modified response with the LLM to generate a coherent final response
    try:
        final_prompt = f"""
        Based on the following data and analysis, provide a coherent response to the original prompt.
        Remember to only use information that is actually present in the data.
        Do not make up or assume any information that is not explicitly provided.
        
        Original prompt: {prompt}
        
        Data and analysis:
        {response}
        """
        final_response = await asyncio.to_thread(llm.get_response, final_prompt)
    except Exception as e:
        return f"Error: {str(e)}"
    
    return final_response
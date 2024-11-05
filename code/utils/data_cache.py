from .cache_config import cache, cache_key
from utils.data_router import get_schema, get_summary, get_sample, get_column_stats, get_value_counts, sum_single_column, detect_outliers


def cached_get_schema():
    """
    Retrieve the schema from the cache if available, otherwise fetch it and store it in the cache.

    This function attempts to get the schema from the cache using a predefined cache key. If the schema
    is not found in the cache, it fetches the schema using the `get_schema` function, stores it in the
    cache, and then returns the schema.

    Returns:
        The schema object, either retrieved from the cache or fetched and then cached.
    """
    key = cache_key("get_schema")
    result = cache.get(key)
    if result is None:
        result = get_schema()
        cache.set(key, result)
    return result

def cached_get_summary():
    """
    Retrieve the summary from the cache if available, otherwise compute it,
    store it in the cache, and return the result.

    This function uses a cache to store the result of the `get_summary` function
    to avoid recomputing it multiple times. If the result is not found in the cache,
    it calls `get_summary` to compute the result, stores it in the cache, and then
    returns the result.

    Returns:
        The summary data, either retrieved from the cache or computed by `get_summary`.
    """
    key = cache_key("get_summary")
    result = cache.get(key)
    if result is None:
        result = get_summary()
        cache.set(key, result)
    return result

# Wrapper for data retrieval functions
def cached_data_retrieval(func_name, *args, **kwargs):
    """
    Retrieve data from cache or execute the specified function and cache its result.

    This function checks if the result of a specified function call is already cached.
    If it is, the cached result is returned. If not, the function is executed, its result
    is cached, and then returned.

    Parameters:
    func_name (str): The name of the function to be executed if the result is not cached.
                     Supported functions are "get_sample", "get_column_stats", "get_value_counts",
                     "sum_single_column", and "detect_outliers".
    *args: Variable length argument list to be passed to the specified function.
    **kwargs: Arbitrary keyword arguments to be passed to the specified function.

    Returns:
    result: The result of the specified function, either retrieved from cache or newly computed.

    Raises:
    ValueError: If the specified function name is not supported.
    """
    key = cache_key(func_name, *args, **kwargs)
    result = cache.get(key)
    if result is None:
        if func_name == "get_sample":
            result = get_sample(*args, **kwargs)
        elif func_name == "get_column_stats":
            result = get_column_stats(*args, **kwargs)
        elif func_name == "get_value_counts":
            result = get_value_counts(*args, **kwargs)
        elif func_name == "sum_single_column":
            result = sum_single_column(*args, **kwargs)
        elif func_name == "detect_outliers":
            result = detect_outliers(*args, **kwargs)
        else:
            raise ValueError(f"Unknown function: {func_name}")
        cache.set(key, result)
    return result
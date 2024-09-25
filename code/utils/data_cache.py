from .cache_config import cache, cache_key
from utils.data_router import get_schema, get_summary, get_sample, get_column_stats, get_value_counts, sum_single_column, detect_outliers


def cached_get_schema():
    key = cache_key("get_schema")
    result = cache.get(key)
    if result is None:
        result = get_schema()
        cache.set(key, result)
    return result

def cached_get_summary():
    key = cache_key("get_summary")
    result = cache.get(key)
    if result is None:
        result = get_summary()
        cache.set(key, result)
    return result

# Wrapper for data retrieval functions
def cached_data_retrieval(func_name, *args, **kwargs):
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
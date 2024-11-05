from fuzzywuzzy import process
from functools import wraps, lru_cache


def get_best_match(column_name: str, columns: list) -> str:
    """
    Finds the best matching column name from a list of columns using fuzzy matching.

    Args:
        column_name (str): The column name to match.
        columns (list): A list of column names to search within.

    Returns:
        str: The best matching column name.

    Raises:
        ValueError: If no good match is found based on the threshold score.
    """
    best_match, score = process.extractOne(column_name, columns)
    if score >= 80: 
        return best_match
    else:
        raise ValueError(f"No good match found for column: {column_name}")

def apply_fuzzy_matching(*args_to_match):
    """
    A decorator to apply fuzzy matching to the specified arguments of a function.
    
    This decorator modifies the specified arguments by finding the best match 
    for each argument in the DataFrame's columns using a fuzzy matching algorithm.
    
    Args:
        *args_to_match: Variable length argument list. The names of the arguments 
                        to apply fuzzy matching to.
    
    Returns:
        A decorator that applies fuzzy matching to the specified arguments of the 
        decorated function.
    
    Example:
        @apply_fuzzy_matching('column1', 'column2')
        def my_function(df, column1, column2):
            # Function implementation
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(df, *args, **kwargs):
            columns = df.columns.tolist()
            matched_args = []
            for arg, arg_name in zip(args, args_to_match):
                if arg_name in kwargs:
                    kwargs[arg_name] = get_best_match(kwargs[arg_name], columns)
                else:
                    matched_args.append(get_best_match(arg, columns))
            return func(df, *matched_args, **kwargs)
        return wrapper
    return decorator

@lru_cache(maxsize=None)
def get_best_match_cached(key, columns):
    """
    Retrieves the best match for a given key from a cache, or computes it if not cached.

    Args:
        key (str): The key to match against.
        columns (list): A list of columns to search for the best match.

    Returns:
        The best match for the given key from the specified columns.
    """
    return get_best_match(key, tuple(columns))  

def fuzzy_getitem(self, key):
    """
    Retrieve an item from the object using a key with fuzzy matching.

    If the exact key is found in the object's columns, the corresponding item is returned.
    If the exact key is not found, the function attempts to find the best match for the key
    among the columns using a cached fuzzy matching function and returns the item corresponding
    to the best match.

    Parameters:
    key (str): The key to search for in the object's columns.

    Returns:
    object: The item corresponding to the exact key or the best fuzzy match.
    """
    if key in self.columns:
        return self[key]
    else:
        best_match = get_best_match_cached(key, tuple(self.columns))
        return self[best_match]
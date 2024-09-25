from fuzzywuzzy import process
from functools import wraps

def get_best_match(column_name: str, columns: list) -> str:
    best_match, score = process.extractOne(column_name, columns)
    if score >= 80:  # You can adjust the threshold as needed
        return best_match
    else:
        raise ValueError(f"No good match found for column: {column_name}")

def apply_fuzzy_matching(*args_to_match):
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
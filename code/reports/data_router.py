import requests
import sys

def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr, flush=True)
    sys.stderr.flush()

def get_schema():
    try:
        response = requests.get('http://localhost:8000/schema')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Error getting schema: {str(e)}")
        return {}

def get_summary():
    try:
        response = requests.get('http://localhost:8000/summary')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Error getting summary: {str(e)}")
        return {}

def get_sample(n=5):
    try:
        response = requests.get(f'http://localhost:8000/sample?n={n}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Error getting sample: {str(e)}")
        return []

def get_column_stats(column_name):
    try:
        response = requests.get(f'http://localhost:8000/column_stats/{column_name}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Error getting column stats: {str(e)}")
        return {}

def get_value_counts(column_name):
    try:
        response = requests.get(f'http://localhost:8000/value_counts/{column_name}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Error getting value counts: {str(e)}")
        return {}

def sum_single_column(column_name):
    try:
        response = requests.get(f'http://localhost:8000/sum_single_column/{column_name}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Error getting sum of column: {str(e)}")
        return {}

def detect_outliers(column_name):
    try:
        response = requests.get(f'http://localhost:8000/outliers/{column_name}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Error detecting outliers: {str(e)}")
        return {}
    
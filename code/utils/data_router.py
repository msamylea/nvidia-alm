import requests
import sys
import os

# Get the base URL for API requests
def get_api_url():
    """
    Constructs the API URL using a proxy prefix from environment variables.

    The function retrieves the proxy prefix from the environment variable 'PROXY_PREFIX'.
    If the environment variable is not set, it defaults to '/projects/nvidia-alm/applications/dash-app'.
    It ensures that the proxy prefix ends with a '/' and then constructs the full API URL
    by appending 'api' to the proxy prefix and prefixing it with 'http://localhost:10000'.

    Returns:
        str: The constructed API URL.
    """
    proxy_prefix = os.getenv('PROXY_PREFIX', '/projects/nvidia-alm/applications/dash-app')
    if not proxy_prefix.endswith('/'):
        proxy_prefix += '/'
    return f"http://localhost:10000{proxy_prefix}api"

API_BASE = get_api_url()

def get_schema():
    """
    Fetches the schema from the API.

    This function constructs the URL for the schema endpoint using the API_BASE
    constant, sends a GET request to the endpoint, and returns the JSON response.
    If an error occurs during the request, it logs the error to stderr and returns
    an empty dictionary.

    Returns:
        dict: The JSON response from the schema endpoint if the request is successful,
              otherwise an empty dictionary.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    try:
        url = f"{API_BASE}/schema"
        print(f"Requesting schema from: {url}")  # Debug logging
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting schema: {str(e)}", file=sys.stderr)
        return {}

def get_summary():
    """
    Fetches a summary from the API.

    Makes a GET request to the summary endpoint of the API and returns the JSON response.
    If an error occurs during the request, it logs the error to stderr and returns an empty dictionary.

    Returns:
        dict: The JSON response from the API if the request is successful, otherwise an empty dictionary.
    """
    try:
        url = f"{API_BASE}/summary"
        print(f"Requesting summary from: {url}")  # Debug logging
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting summary: {str(e)}", file=sys.stderr)
        return {}

def get_sample(n=5):
    """
    Fetches a sample of data from the API.

    Args:
        n (int, optional): The number of samples to fetch. Defaults to 5.

    Returns:
        list: A list of sample data if the request is successful, otherwise an empty list.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    try:
        url = f"{API_BASE}/sample?n={n}"
        print(f"Requesting sample from: {url}")  # Debug logging
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting sample: {str(e)}", file=sys.stderr)
        return []

def get_column_stats(column_name):
    """
    Fetches statistics for a specified column from API.

    Args:
        column_name (str): The name of the column for which to retrieve statistics.

    Returns:
        dict: A dictionary containing the column statistics if the request is successful.
              Returns an empty dictionary if there is an error during the request.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    try:
        url = f"{API_BASE}/column_stats/{column_name}"
        print(f"Requesting column stats from: {url}")  # Debug logging
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting column stats: {str(e)}", file=sys.stderr)
        return {}

def get_value_counts(column_name, top_n=10):
    """
    Fetches the value counts for a specified column from API.

    Args:
        column_name (str): The name of the column for which to fetch value counts.
        top_n (int, optional): The number of top values to retrieve. Defaults to 10.

    Returns:
        dict: A dictionary containing the value counts for the specified column.
              Returns an empty dictionary if there is an error during the request.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    try:
        url = f"{API_BASE}/value_counts/{column_name}?top_n={top_n}"
        print(f"Requesting value counts from: {url}")  # Debug logging
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting value counts: {str(e)}", file=sys.stderr)
        return {}
    
def sum_single_column(column_name):
    """
    Fetches the sum of a single column from API.

    Args:
        column_name (str): The name of the column to sum.

    Returns:
        dict: A dictionary containing the sum of the column if the request is successful.
              An empty dictionary is returned if there is an error during the request.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    try:
        url = f"{API_BASE}/sum_single_column/{column_name}"
        print(f"Requesting column sum from: {url}")  # Debug logging
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting column sum: {str(e)}", file=sys.stderr)
        return {}

def detect_outliers(column_name):
    """
    Detects outliers for a given column by making a request to API.

    Args:
        column_name (str): The name of the column for which to detect outliers.

    Returns:
        dict: A dictionary containing the outliers data if the request is successful.
              An empty dictionary is returned if there is an error during the request.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    try:
        url = f"{API_BASE}/outliers/{column_name}"
        print(f"Requesting outliers from: {url}")  # Debug logging
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error detecting outliers: {str(e)}", file=sys.stderr)
        return {}
import requests
import sys


def get_schema():
    try:
        response = requests.get('http://localhost:8000/schema')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {}

def get_summary():
    try:
        response = requests.get('http://localhost:8000/summary')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {}

def get_sample(n=5):
    try:
        response = requests.get(f'http://localhost:8000/sample?n={n}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return []

def get_column_stats(column_name):
    try:
        response = requests.get(f'http://localhost:8000/column_stats/{column_name}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {}

def get_value_counts(column_name, top_n=10):
    try:
        response = requests.get(f'http://localhost:8000/value_counts/{column_name}?top_n={top_n}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {}
    
def sum_single_column(column_name):
    try:
        response = requests.get(f'http://localhost:8000/sum_single_column/{column_name}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {}

def detect_outliers(column_name):
    try:
        response = requests.get(f'http://localhost:8000/outliers/{column_name}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {}
    
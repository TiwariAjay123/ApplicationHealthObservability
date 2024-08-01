import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuration
LOKI_URL = 'http://your-loki-url:3100'
PROMETHEUS_URL = 'http://your-prometheus-url:9090'
LOKI_QUERY = '{job="your-job"}'
PROMETHEUS_QUERIES = {
    'cpu_usage': 'rate(container_cpu_usage_seconds_total{container_name="your-container"}[1m])',
    'memory_usage': 'container_memory_usage_bytes{container_name="your-container"}',
}

# Function to query Loki logs
def query_loki(query, start, end):
    url = f"{LOKI_URL}/loki/api/v1/query_range"
    params = {
        'query': query,
        'start': start,
        'end': end,
        'limit': 1000,
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['data']['result']

# Function to query Prometheus metrics
def query_prometheus(query, time):
    url = f"{PROMETHEUS_URL}/api/v1/query"
    params = {
        'query': query,
        'time': time,
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['data']['result']

# Function to analyze logs
def analyze_logs(logs):
    error_count = sum(1 for stream in logs for entry in stream['values'] if 'error' in entry[1].lower())
    return error_count

# Function to analyze metrics
def analyze_metrics(metrics):
    cpu_usage = float(metrics['cpu_usage'][0]['value'][1])
    memory_usage = float(metrics['memory_usage'][0]['value'][1])
    return cpu_usage, memory_usage

# Main function to display application health
def display_application_health():
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=5)
    end_timestamp = int(end_time.timestamp() * 1e9)
    start_timestamp = int(start_time.timestamp() * 1e9)

    # Query Loki logs
    logs = query_loki(LOKI_QUERY, start_timestamp, end_timestamp)
    error_count = analyze_logs(logs)

    # Query Prometheus metrics
    current_time = int(end_time.timestamp())
    metrics = {key: query_prometheus(query, current_time) for key, query in PROMETHEUS_QUERIES.items()}
    cpu_usage, memory_usage = analyze_metrics(metrics)

    # Display application health
    print("Application Health Report")
    print("-------------------------")
    print(f"Error count in logs (last 5 minutes): {error_count}")
    print(f"CPU Usage: {cpu_usage:.2f}")
    print(f"Memory Usage: {memory_usage / (1024 ** 2):.2f} MB")

if __name__ == "__main__":
    display_application_health()

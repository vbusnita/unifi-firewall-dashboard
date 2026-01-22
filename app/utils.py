import os
import base64
import requests
import json
from dotenv import load_dotenv

def fetch_firewall_drops(range_seconds=86400, limit=1000):
    """
    Fetch recent firewall drop logs from Graylog.
    Returns list of dicts with at least {'timestamp', 'source', 'message'}
    """
    load_dotenv()
    graylog_url = os.getenv('GRAYLOG_URL')
    graylog_token = os.getenv('GRAYLOG_API_TOKEN')

    if not graylog_url or not graylog_token:
        print("Error: Missing GRAYLOG_URL or GRAYLOG_API_TOKEN in .env")
        return []

    auth_str = f"{graylog_token}:token"
    b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Accept": "application/json"
    }

    params = {
        "query": 'message:WAN_LOCAL-D OR message:"Log WAN to Gateway Drops"',
        "range": range_seconds,
        "limit": limit,
        "sort": "timestamp:desc"
    }

    url = f"{graylog_url.rstrip('/')}/api/search/universal/relative"

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Graylog v6 usually puts messages here
        messages = data.get('messages', [])

        # Normalize to simple list of dicts
        normalized = []
        for item in messages:
            msg = item.get('message', {})
            normalized.append({
                'timestamp': msg.get('timestamp'),
                'source': msg.get('source'),
                'message': msg.get('message')
            })

        print(f"Fetched {len(normalized)} firewall drop logs")
        return normalized

    except requests.exceptions.HTTPError as e:
        print(f"Graylog HTTP error: {e.response.status_code} - {e.response.text[:500]}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

if __name__ == "__main__":
    logs = fetch_firewall_drops()
    if logs:
        print("\nFirst log example:")
        print(json.dumps(logs[0], indent=2))
    else:
        print("No logs returned — check query, time range, or token permissions.")
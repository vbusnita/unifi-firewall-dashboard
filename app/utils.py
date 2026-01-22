import os
import base64
import requests
import json
import re
from collections import Counter
from dotenv import load_dotenv

def fetch_firewall_drops(range_seconds=86400, limit=1000):
    """
    Fetch recent firewall drop logs from Graylog.
    Returns list of dicts: [{'timestamp': str, 'source': str, 'message': str}, ...]
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
        messages = data.get('messages', [])

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

def parse_firewall_drops(raw_logs):
    """
    Parse raw Graylog messages into structured drop events + stats.
    Returns (parsed_list, stats_dict)
    """
    parsed = []

    # Extremely permissive pattern: match the core signature + loose field capture
    pattern = re.compile(
        r'\[WAN_LOCAL-D-(?P<rule_id>\d+)\].*?'
        r'DESCR="(?P<descr>[^"]+)"\s*'
        r'IN=\S*\s*OUT=\S*\s*'
        r'(?:MAC=[^ ]+\s*)?'  # optional MAC
        r'(?:.*?)'            # skip any junk
        r'SRC=(?P<src_ip>[^ ]+)\s*'
        r'DST=(?P<dst_ip>[^ ]+)\s*'
        r'(?:LEN=\d+\s+TOS=\S+\s+PREC=\S+\s+TTL=\d+\s+ID=\d+\s+DF\s+)?'  # optional fixed block
        r'(?:PROTO=(?P<proto>\S+)\s*)?'
        r'(?:SPT=(?P<src_port>\d+)\s*)?'
        r'(?:DPT=(?P<dst_port>\d+)\s*)?'
    )

    for log in raw_logs:
        message = log.get('message', '')
        match = pattern.search(message)
        if match and match.group('src_ip') and match.group('dst_ip'):
            parsed.append({
                'timestamp': log.get('timestamp'),
                'rule_id': match.group('rule_id'),
                'descr': match.group('descr'),
                'src_ip': match.group('src_ip'),
                'dst_ip': match.group('dst_ip'),
                'proto': match.group('proto') or 'UNKNOWN',
                'src_port': int(match.group('src_port')) if match.group('src_port') else None,
                'dst_port': int(match.group('dst_port')) if match.group('dst_port') else None,
                'raw_message': message
            })

    if not parsed:
        print("No logs matched the regex pattern. Sample message:")
        if raw_logs:
            print(raw_logs[0].get('message', 'No message field'))
        return [], {'total_blocks': 0, 'top_src_subnets': {}, 'top_dst_ports': {}}

    # Stats
    total_blocks = len(parsed)

    src_subnets = Counter()
    for p in parsed:
        ip = p['src_ip']
        if ip:
            subnet = '.'.join(ip.split('.')[:3]) + '.0/24'
            src_subnets[subnet] += 1

    dst_ports = Counter(p['dst_port'] for p in parsed if p['dst_port'] is not None)

    stats = {
        'total_blocks': total_blocks,
        'top_src_subnets': dict(src_subnets.most_common(5)),
        'top_dst_ports': dict(dst_ports.most_common(10))
    }

    return parsed, stats

if __name__ == "__main__":
    print("Running test...")
    raw = fetch_firewall_drops(limit=200)
    parsed, stats = parse_firewall_drops(raw)

    print(f"\nParsed {len(parsed)} valid drop events")
    print("Stats:")
    print(json.dumps(stats, indent=2))

    if parsed:
        print("\nFirst parsed event:")
        print(json.dumps(parsed[0], indent=2))
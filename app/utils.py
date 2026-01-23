# utils.py (final, with prompt extracted to ai_prompts.py + other polishes)
import os
import base64
import requests
import json
import re
from collections import Counter
from dotenv import load_dotenv
from app.normalizer import normalize_logs
from app.ai_prompt import get_summary_prompt  # New import for extracted prompt
from datetime import datetime


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
            # Real Graylog: item = {'message': {actual fields}}
            # Mock/simple: item = {actual fields}
            msg = item.get('message', item)  # fallback to item itself if no nested 'message'
            normalized.append({
                'timestamp': msg.get('timestamp'),
                'source': msg.get('source'),
                'message': msg.get('message')   # real nested message text
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

def log_tokens(input_tokens, output_tokens, cost_est):
    """Log AI token usage to console and file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | Input: {input_tokens} | Output: {output_tokens} | Est cost: ${cost_est:.6f}\n"
    
    # Console
    print(f"AI tokens logged: {line.strip()}")
    
    # File (append mode)
    try:
        with open("ai_token_log.txt", "a") as f:
            f.write(line)
    except Exception as e:
        print(f"Warning: Could not write to ai_token_log.txt: {e}")


def generate_ai_summary(parsed_logs, use_normalizer=True, log_to_file=True, max_logs=100):
    """
    Generate AI summary from parsed logs (with optional normalizer).
    Returns {'summary': str, 'input_tokens': int, 'output_tokens': int, 'cost_est': float}
    """
    if not parsed_logs:
        print("No parsed logs; returning default summary.")
        return {'summary': 'No recent threats.', 'input_tokens': 0, 'output_tokens': 0, 'cost_est': 0.0}

    load_dotenv()
    grok_api_key = os.getenv('GROK_API_KEY')

    if not grok_api_key:
        print("Error: Missing GROK_API_KEY in .env")
        return {'summary': '', 'input_tokens': 0, 'output_tokens': 0, 'cost_est': 0.0}

    if use_normalizer:
        batch_text = normalize_logs(parsed_logs)
        approx_tokens_before = sum(len(p['raw_message']) for p in parsed_logs) // 4  # rough char-to-token
        approx_tokens_after = len(batch_text) // 4
        print(f"[Token Opt] Before norm: ~{approx_tokens_before} tokens; After: ~{approx_tokens_after} ({(approx_tokens_after / approx_tokens_before * 100) if approx_tokens_before else 0:.1f}% of original)")
    else:
        batch = [p['raw_message'] for p in parsed_logs[:max_logs]]
        batch_text = '\n'.join(batch)

    prompt = get_summary_prompt(batch_text)  # Extracted to ai_prompts.py

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {grok_api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "grok-4-1-fast-reasoning",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        summary = result['choices'][0]['message']['content'].strip()
        usage = result['usage']
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)

        cost_est = (input_tokens / 1_000_000 * 0.20) + (output_tokens / 1_000_000 * 0.50)

        if log_to_file:
            log_tokens(input_tokens, output_tokens, cost_est)

        print(f"AI summary (normalizer={use_normalizer}): Input {input_tokens}, Output {output_tokens}, Est ${cost_est:.6f}")

        return {
            'summary': summary,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_est': cost_est
        }

    except requests.exceptions.HTTPError as e:
        print(f"Grok API HTTP error: {e.response.status_code} - {e.response.text[:500]}")
        return {'summary': '', 'input_tokens': 0, 'output_tokens': 0, 'cost_est': 0.0}
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {'summary': '', 'input_tokens': 0, 'output_tokens': 0, 'cost_est': 0.0}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {'summary': '', 'input_tokens': 0, 'output_tokens': 0, 'cost_est': 0.0}

# Test block
if __name__ == "__main__":
    print("Running baseline (no normalizer)...")
    raw = fetch_firewall_drops(limit=200)
    parsed, stats = parse_firewall_drops(raw)

    print(f"\nParsed {len(parsed)} valid drop events")
    print("Stats:")
    print(json.dumps(stats, indent=2))

    # ai_baseline = generate_ai_summary(parsed, use_normalizer=False)
    # print("\nBaseline Summary:")
    # print(ai_baseline['summary'])
    # print(f"Tokens: {ai_baseline['input_tokens']} in / {ai_baseline['output_tokens']} out")
    # print(f"Est cost: ${ai_baseline['cost_est']:.6f}")

    print("\n\nRunning with normalizer...")
    ai_norm = generate_ai_summary(parsed, use_normalizer=True)
    print("\nNormalized Summary:")
    print(ai_norm['summary'])
    print(f"Tokens: {ai_norm['input_tokens']} in / {ai_norm['output_tokens']} out")
    print(f"Est cost: ${ai_norm['cost_est']:.6f}")
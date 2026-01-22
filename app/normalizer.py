from collections import defaultdict


def normalize_logs(parsed_logs, max_groups=50):
    """
    Normalize parsed firewall logs into concise summary text for lower token usage.
    
    Groups events by (src_subnet /24, dst_port, proto) and counts occurrences.
    Returns a multi-line string suitable for AI prompts.
    
    Example output line: "45 UDP probes on DPT=51413 from 173.249.19.0/24"
    """
    groups = defaultdict(int)

    for p in parsed_logs:
        if p.get('src_ip') and p.get('dst_port') and p.get('proto'):
            subnet = '.'.join(p['src_ip'].split('.')[:3]) + '.0/24'
            key = (subnet, p['dst_port'], p['proto'])
            groups[key] += 1

    # Sort by count descending, take top N
    sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)[:max_groups]

    lines = []
    for (subnet, dst_port, proto), count in sorted_groups:
        lines.append(f"{count} {proto} probes on DPT={dst_port} from {subnet}")

    condensed = '\n'.join(lines)
    
    # Optional logging for visibility
    print(f"[Normalizer] Condensed {len(parsed_logs)} logs → {len(lines)} groups")

    return condensed


# Optional: future variants can live here as separate functions
# def normalize_logs_v2(...): ...
# def normalize_logs_simple(...): ...
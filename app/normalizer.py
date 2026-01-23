# normalizer.py (final, as proposed with minor empty handling)
from collections import defaultdict, Counter


def normalize_logs(
    parsed_logs,
    max_groups=30,
    exclude_ports={51413},  # default empty - include all ports
    threat_ports=None
):
    if threat_ports is None:
        threat_ports = {
            22: 5, 23: 5, 3389: 10, 445: 8, 1433: 8, 3306: 6
        }

    if not parsed_logs:
        return "\nTotal normalized events: 0 (from 0 raw)\nThreat score total: 0"

    # Primary grouping: port + proto (preserves volume)
    port_groups = defaultdict(int)
    # Subnet details per port
    subnet_details = defaultdict(list)

    threat_score_total = 0

    for p in parsed_logs:
        dst_port = p.get('dst_port')
        if dst_port is None or dst_port in exclude_ports:
            continue

        proto = p.get('proto', 'UNKNOWN')
        port_key = (dst_port, proto)
        port_groups[port_key] += 1

        subnet = '.'.join(p['src_ip'].split('.')[:3]) + '.0/24' if p.get('src_ip') else 'unknown'
        subnet_details[port_key].append(subnet)

        score = threat_ports.get(dst_port, 1)
        threat_score_total += score

    lines = []

    # Port aggregates
    sorted_ports = sorted(port_groups.items(), key=lambda x: x[1], reverse=True)
    for (dst_port, proto), count in sorted_ports[:max_groups]:
        threat_level = "HIGH" if dst_port in threat_ports and threat_ports[dst_port] >= 8 else \
                       "MEDIUM" if dst_port in threat_ports else "LOW"
        lines.append(f"{count} {proto} probes on DPT={dst_port} ({threat_level})")

        # Top 3 subnets for this port
        subnet_counts = Counter(subnet_details[(dst_port, proto)])  # ← FIXED: Use current (dst_port, proto) as key, not stale 'port_key'
        for subnet, sub_count in subnet_counts.most_common(3):
            lines.append(f"  └─ {sub_count} from {subnet}")

    condensed = '\n'.join(lines)

    summary_stats = f"\nTotal normalized events: {sum(port_groups.values())} (from {len(parsed_logs)} raw)"
    if threat_score_total > 0:
        summary_stats += f"\nThreat score total: {threat_score_total}"

    print(f"[Normalizer] Condensed {len(parsed_logs)} logs → {len(lines)} lines")
    print(summary_stats)

    return condensed + summary_stats
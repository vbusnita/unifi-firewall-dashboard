from collections import defaultdict, Counter


def normalize_logs(
    parsed_logs,
    max_groups=50,
    exclude_ports=None,
    threat_ports=None
):
    if exclude_ports is None:
        exclude_ports = set()  # no exclusion by default

    if threat_ports is None:
        threat_ports = {
            22: 5,      # SSH
            23: 5,      # Telnet
            3389: 10,   # RDP
            445: 8,     # SMB
            1433: 8,    # MSSQL
            3306: 6     # MySQL
        }

    groups = defaultdict(int)
    threat_score_total = 0

    for p in parsed_logs:
        dst_port = p.get('dst_port')
        if dst_port is None or dst_port in exclude_ports:
            continue

        subnet = '.'.join(p['src_ip'].split('.')[:3]) + '.0/24' if p.get('src_ip') else 'unknown'
        proto = p.get('proto', 'UNKNOWN')
        key = (subnet, dst_port, proto)
        groups[key] += 1

        score = threat_ports.get(dst_port, 1)
        threat_score_total += score

    sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)[:max_groups]

    lines = []
    for (subnet, dst_port, proto), count in sorted_groups:
        score = threat_ports.get(dst_port, 1)
        threat_level = "HIGH" if score >= 8 else "MEDIUM" if score >= 3 else "LOW"
        lines.append(f"{count} {proto} probes on DPT={dst_port} ({threat_level}) from {subnet}")

    condensed = '\n'.join(lines)

    summary_stats = f"\nTotal normalized events: {sum(groups.values())} (from {len(parsed_logs)} raw)"
    if threat_score_total > 0:
        summary_stats += f"\nThreat score total: {threat_score_total}"

    print(f"[Normalizer] Condensed {len(parsed_logs)} logs → {len(lines)} groups")
    print(summary_stats)

    return condensed + summary_stats
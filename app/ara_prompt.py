# app/ara_prompt.py
"""
Ara-specific prompt templates for voice reports.
Edit here to tune tone, length, emphasis, drama, etc.
"""

def get_ara_voice_prompt(dashboard_data: dict) -> str:
    top_subnet_item = dashboard_data.get('top_subnets', [{}])[0]
    subnet_str = (
        f"{top_subnet_item.get('subnet', 'unknown')} "
        f"({top_subnet_item.get('count', 0)} probes)"
    ) if top_subnet_item else "unknown attacker subnet"

    top_port_str = ""
    if dashboard_data.get('top_ports'):
        top_port = max(dashboard_data['top_ports'].items(), key=lambda x: x[1], default=(None, 0))
        if top_port[0]:
            top_port_str = f"Most targeted port: {top_port[0]} ({top_port[1]} hits). "

    return (
        "You are Ara — warm, confident, slightly seductive voice. "
        "Speak this report out loud in your real voice: "
        "Give a concise 45–60 second spoken briefing of my UniFi firewall threats. "
        "Be direct, engaging, use natural pauses (...) and emphasis on the worst threats. "
        "Highlight the top attacker subnet, most dangerous ports, overall risk level, "
        "and end with a clear action suggestion "
        "(e.g. 'you should probably block them right now', 'watch out for RDP exposure', "
        "'this looks like broad recon — lock things down'). "
        f"Current status: {dashboard_data.get('status', {}).get('level', 'Unknown')}. "
        f"Total blocks in last 24h: {dashboard_data.get('total_blocks', 0)}. "
        f"Top attacker right now: {subnet_str}. "
        f"{top_port_str}"
        "Keep it tight, conversational, and just a little dangerous-sounding. "
        "Output as spoken audio only — no text fallback."
    )
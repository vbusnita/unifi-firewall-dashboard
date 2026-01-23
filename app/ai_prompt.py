# ai_prompts.py (new file)
def get_summary_prompt(batch_text: str) -> str:
    """
    Returns the structured prompt for AI summary generation.
    This allows easy iteration on prompt engineering without cluttering utils.py.
    """
    return (
    f"Provide a concise plain-English summary of the last 24h UniFi firewall blocks based on this condensed data: {batch_text}. "
    "The data includes counts of probes per port/proto, top source /24 subnets, and a 'Threat score total' (higher for dangerous ports like RDP/3389). "
    "Focus on: top attacking subnets (/24), common targeted ports, potential threats (e.g., RDP on 3389), overall risk level (low/medium/high). "
    "Output 2 to 5 sentences only."
)
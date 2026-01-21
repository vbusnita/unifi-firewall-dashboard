# UniFi Firewall Drops Dashboard

Single-page dashboard that queries Graylog for UXG-Pro firewall drop logs,
parses them, shows stats (blocks count, top IPs/ports), and uses Grok AI for summaries.

## Setup
1. `source venv/bin/activate`
2. `pip install -r requirements.txt`
3. Fill `.env` with keys
4. `python run.py`

Runs on http://127.0.0.1:5000

## Structure
- prd.md          → product requirements & plan
- app/            → Flask app code
- templates/      → HTML/Jinja templates
- static/         → CSS/JS if needed
- run.py          → entry point

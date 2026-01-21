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
```text
unifi-firewall-dashboard/
├── .env                  # secrets - gitignored
├── .gitignore
├── prd.md                # product requirements & plan
├── README.md
├── requirements.txt
├── setup.sh              # one-command environment bootstrap
├── run.py                # Flask entry point (we'll fill this)
├── app/
│   ├── __init__.py
│   ├── routes.py         # Flask routes
│   └── utils.py          # API fetch, parsing, stats, AI summary
├── templates/
│   └── index.html        # main dashboard template (Jinja)
└── static/               # optional CSS/JS
    └── style.css
```


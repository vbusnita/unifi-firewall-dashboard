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
unifi-firewall-dashboard/
├── .env                  # secrets - gitignored
├── .gitignore
├── prd.md                # paste our latest version here
├── README.md
├── requirements.txt
├── setup.sh              # setup script for the project  
├── run.py                # we'll fill this soon
├── app/
│   ├── __init__.py
│   ├── routes.py
│   └── utils.py          # parsing, api fetch, etc.
├── templates/
│   └── index.html        # main dashboard template
└── static/               # css/js if needed
    └── style.css

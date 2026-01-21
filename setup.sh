#!/usr/bin/env bash
# setup.sh - Idempotent environment setup

set -euo pipefail

echo "=== Setting up unifi-firewall-dashboard environment ==="

# Exit early if not in project dir (basic sanity)
if [[ ! -f "prd.md" ]]; then
    echo "Error: Please run this from the unifi-firewall-dashboard root directory"
    exit 1
fi

# Python check
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Install Python 3.12+."
    exit 1
fi

# Venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi


# Pip + deps
echo "Installing dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "No requirements.txt found — installing core packages"
    pip install flask requests python-dotenv pandas
    pip freeze > requirements.txt
fi

# .env template
if [ ! -f ".env" ]; then
    echo "Creating .env template..."
    cat << 'EOF' > .env
GRAYLOG_URL=http://10.0.1.42:9000
GRAYLOG_API_TOKEN=your-graylog-read-token-here
GROK_API_KEY=your-xai-api-key-here
FLASK_SECRET_KEY=replace-this-with-a-random-long-string
EOF
    echo ".env created — edit it with real values!"
else
    echo ".env already exists — skipping creation"
fi

echo ""
echo "Setup complete!"
echo "Next:"
echo "  1. Edit .env with your real tokens"
echo "  2. source venv/bin/activate   (activate your environment)"
echo "  3. python run.py   (or flask --app run.py run)"
echo ""

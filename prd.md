# UniFi Network Status Dashboard

## Overview
A single-page web dashboard that queries Graylog for firewall drop logs from UniFi UXG-Pro, filters for last 24 hours, parses key events (blocked connections), and uses Grok AI to generate human-readable summaries (e.g., "Blocked 45 TCP probes on port 8443 from scanners"). Displays overview stats, top threats, and timeline. Logs are raw iptables style from /var/log/ulog/syslogemu.log exported via SIEM.

## Goals
- At-a-glance home network security insight without manual digging.
- Success: Loads <5s, summarizes 100+ logs accurately, runs locally/self-sustained.

## Tech Stack
- Backend: Python 3.12+ (Flask, requests for Graylog API, re for parsing, pandas for stats)
- AI: xAI Grok API
- Frontend: Simple HTML/CSS/JS (Jinja templates, HTMX optional for auto-refresh)
- Config: .env for GRAYLOG_URL, GRAYLOG_API_TOKEN, GROK_API_KEY

## Features

1. **Log Ingestion**
   - Description: Query Graylog API for messages with "[WAN_LOCAL-D" OR "Log WAN to Gateway Drops" from last 24h (relative timerange 86400s).
   - Acceptance Criteria: Fetches JSON with timestamp, source, full message; handles 1000+ results.
   - Tests: Mock API → returns list of messages.

2. **Log Parsing & Filtering**
   - Description: Parse raw message lines like "[WAN_LOCAL-D-40000] DESCR="Log WAN to Gateway Drops" IN=eth0 ... SRC=... DST=... PROTO=... SPT=... DPT=...".
   - Extract: timestamp, src_ip, dst_ip (DST=your WAN), proto, src_port, dst_port, rule_id.
   - Filter: Only WAN_LOCAL drops, last 24h, exclude internal SRC (e.g., 192.168.x).
   - Acceptance Criteria: Structured list of dicts; ignores non-drop lines.
   - Tests: Sample line → correct fields.

3. **AI-Powered Summary**
   - Description: Batch 50-200 parsed events, send to Grok API: "Summarize these UniFi firewall blocks last 24h: top attacking IPs (group by /24 subnet), common targeted ports, potential threats (e.g., RDP scans on 3389), overall status. Concise, plain English."
   - Acceptance Criteria: Readable summary (e.g., "45 blocks, mostly TCP on 8443 from 167.94.138.0/24 scanners — network secure").
   - Tests: Mock events → API call succeeds.

4. **Dashboard Display**
   - Description: Flask route / with template: Status color (green <50 blocks, yellow 50-200, red >200), total blocks, top 5 src subnets, top 10 dst ports (table/chart), AI summary, simple timeline (blocks per hour).
   - Auto-refresh: Every 5min via JS/HTMX.
   - Acceptance Criteria: Responsive, loads data on request.
   - Tests: Browser renders stats/summary.

5. **Configuration & Security**
   - Description: .env for API keys/URLs; local run only (no public).
   - Acceptance Criteria: Keys not hardcoded.

## Milestones
1. API fetch + parse drops.
2. Stats aggregation + AI summary.
3. Flask dashboard.
4. Tests + polish.

## Risks/Notes
- Log volume: Cap queries at 1000 results; rate-limit if needed.
- Format: Raw iptables; watch for CEF if IPS blocks included.
- Open questions: Status thresholds, chart lib (e.g., Chart.js)?

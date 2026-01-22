# UniFi Firewall Drops Dashboard

## Overview
Single-page Flask dashboard that queries Graylog for UXG-Pro firewall drop logs, parses them, shows basic stats (total blocks, top attacking subnets, common targeted ports), and uses Grok AI to generate a concise natural-language summary of the last 24 hours of activity.

## Goals
- Quick at-a-glance view of "is my network being attacked right now?"
- Low maintenance, runs locally on MacBook
- Uses only open-source/free tools where possible

## Non-functional Requirements
- Runs on localhost:5000
- Auto-refreshes every 5 minutes (JS timer)
- Graceful handling when no logs or Graylog down (fallback message, retry button)
- Secure: no public exposure, API keys in .env only
- Unit tests for each feature (using pytest)
- Token tracking for AI calls: log input/output tokens to console, show total in UI footer
- Cost optimization: Normalizer to truncate/condense log batches before AI prompt

## Tech Choices
- Backend: Flask
- Env: python-dotenv
- HTTP: requests
- Parsing: re + pandas for stats
- AI: xAI Grok API (grok-4-1-fast-reasoning)
- Data source: Graylog REST API (/api/search/universal/relative)
- Logs format: raw iptables ulog style (e.g. [WAN_LOCAL-D-40000] DESCR=... SRC=... DPT=...)
- UI: Dark-mode default (sleek, xAI-inspired: high-contrast blacks/grays, minimal accents; no heavy libs, use vanilla CSS + Chart.js for charts)
- Testing: pytest for unit tests

## Features

1. **Log Ingestion**
   - Description: Query Graylog API for messages with "[WAN_LOCAL-D" OR "Log WAN to Gateway Drops" from last 24 hours.
   - Acceptance Criteria: Fetches JSON with at least timestamp, source, full message; handles 1000+ results.
   - Tests: Unit tests for successful fetch, error cases (bad token, no results, timeout).

2. **Log Parsing & Filtering**
   - Description: Parse raw message lines like "UXG Pro Pro [WAN_LOCAL-D-40000] DESCR=\"Log WAN to Gateway Drops\" ... SRC=... DST=... PROTO=... SPT=... DPT=...".
   - Extract: timestamp, rule_id (e.g. 40000), src_ip, dst_ip, proto, src_port, dst_port.
   - Filter: Only valid WAN_LOCAL drops (regex match required).
   - Stats: total_blocks, top_src_subnets (/24 grouping for CGNAT), top_dst_ports (top 10).
   - Acceptance Criteria: 90%+ match rate on real fetches; ignores noise.
   - Tests: Unit tests for parsing sample lines, edge cases (missing fields).

3. **AI-Powered Summary**
   - Description: Batch parsed events (up to 200), normalize/condense (e.g., group by subnet/port for "pure signal"), send to Grok API with prompt: "Summarize these UniFi firewall blocks last 24h: top IPs (group /24), common ports, potential threats (e.g., RDP on 3389), overall status. Concise, plain English."
   - Normalization: Dedupe/summarize similar events (e.g., "45 probes on DPT=51413 from 167.94.x.x") to cut tokens 50-80%.
   - Track: Input/output tokens per call (log to console/UI).
   - Acceptance Criteria: Readable summary (2-5 sentences); handles empty batch ("No recent threats").
   - Tests: Unit tests for normalization, mock AI call.

4. **Dashboard Display**
   - Description: Flask route / with Jinja template: Dark-mode UI (sleek xAI-style: black/gray background, white/accent text, simple cards/tables, Chart.js bar charts for ports/subnets).
     - Status card (color-coded green/yellow/red based on total blocks: <50 green, 50-300 yellow, >300 red)
     - Total blocks count
     - Top 5 src subnets table
     - Top 10 dst ports chart
     - AI summary text
     - Simple timeline (blocks per hour bar chart)
     - Token usage footer (e.g., "Last AI call: 1234 in / 567 out tokens")
   - Auto-refresh: JS setInterval to reload every 5 min.
   - Acceptance Criteria: Responsive on MacBook, loads data on request.
   - Tests: Integration test for route response, mock data.

5. **Configuration & Security**
   - Description: .env for keys; local run only.
   - Acceptance Criteria: App starts without hardcoded secrets.

## Milestones
1. Fetch + parse + stats (core backend)
2. AI summary + normalization
3. Flask route + UI (dark-mode sleek)
4. Tests + polish

## Risks/Notes
- Log volume: Cap at 1000/query; normalize to <5k tokens for AI.
- Graylog downtime: Cache last fetch in local JSON if >1h old.
- Open: Add GeoIP for top attackers? Email alerts on red status?
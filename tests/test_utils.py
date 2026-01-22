import pytest
from unittest.mock import Mock
import requests_mock
from app.utils import fetch_firewall_drops, parse_firewall_drops

# Sample raw log from your real output
SAMPLE_RAW_LOG = {
    "timestamp": "2026-01-22T21:44:47.000Z",
    "source": "UXG",
    "message": 'UXG Pro Pro [WAN_LOCAL-D-40000] DESCR="Log WAN to Gateway Drops" IN=eth0 OUT= MAC=e4:38:83:9a:f0:63:0c:ac:8a:e5:fe:54:08:00 SRC=173.249.19.73 DST=70.24.240.148 LEN=125 TOS=00 PREC=0x00 TTL=55 ID=15036 DF PROTO=UDP SPT=12023 DPT=51413 LEN=105 MARK=1c0000'
}

SAMPLE_RESPONSE = {
    "messages": [
        {
            "message": SAMPLE_RAW_LOG  # nested like real Graylog
        },
        {
            "message": SAMPLE_RAW_LOG
        }
    ]
}

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GRAYLOG_URL", "http://fake.graylog:9000")
    monkeypatch.setenv("GRAYLOG_API_TOKEN", "fake-token-123")

def test_fetch_firewall_drops_success(mock_env, requests_mock):
    requests_mock.get(
        "http://fake.graylog:9000/api/search/universal/relative",
        json=SAMPLE_RESPONSE,
        status_code=200
    )

    logs = fetch_firewall_drops(range_seconds=3600, limit=10)
    assert len(logs) == 2
    assert logs[0]["timestamp"] == "2026-01-22T21:44:47.000Z"
    assert "WAN_LOCAL-D-40000" in logs[0]["message"]

def test_fetch_firewall_drops_failure_401(mock_env, requests_mock):
    requests_mock.get(
        "http://fake.graylog:9000/api/search/universal/relative",
        status_code=401,
        json={"error": "Unauthorized"}
    )

    logs = fetch_firewall_drops()
    assert logs == []

def test_parse_firewall_drops():
    raw_logs = [SAMPLE_RAW_LOG]
    parsed, stats = parse_firewall_drops(raw_logs)

    assert len(parsed) == 1
    p = parsed[0]
    assert p["rule_id"] == "40000"
    assert p["src_ip"] == "173.249.19.73"
    assert p["dst_port"] == 51413
    assert p["proto"] == "UDP"

    assert stats["total_blocks"] == 1
    assert "173.249.19.0/24" in stats["top_src_subnets"]
    assert stats["top_dst_ports"] == {51413: 1}

def test_parse_no_match():
    raw_logs = [{"message": "Some unrelated log line"}]
    parsed, stats = parse_firewall_drops(raw_logs)

    assert len(parsed) == 0
    assert stats["total_blocks"] == 0
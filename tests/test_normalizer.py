import pytest
from app.normalizer import normalize_logs

@pytest.fixture
def sample_parsed_logs():
    return [
        {'src_ip': '173.249.33.72', 'dst_port': 51413, 'proto': 'UDP'},
        {'src_ip': '173.249.33.72', 'dst_port': 51413, 'proto': 'UDP'},
        {'src_ip': '207.180.192.206', 'dst_port': 8443, 'proto': 'TCP'},
        {'src_ip': '5.189.160.21', 'dst_port': 51413, 'proto': 'UDP'},
    ]

def test_normalize_logs_basic(sample_parsed_logs):
    # Override default exclusion to test with 51413 included
    condensed = normalize_logs(sample_parsed_logs, max_groups=10, exclude_ports=set())
    assert "3 UDP probes on DPT=51413 (LOW)" in condensed
    assert "2 from 173.249.33.0/24" in condensed  # for UDP
    assert "1 from 5.189.160.0/24" in condensed   # for UDP
    assert "1 TCP probes on DPT=8443 (LOW)" in condensed
    assert "1 from 207.180.192.0/24" in condensed  # for TCP

def test_normalize_logs_excludes_noise(sample_parsed_logs):
    condensed = normalize_logs(sample_parsed_logs, exclude_ports={51413})
    assert "51413" not in condensed
    assert "8443" in condensed
    assert "Total normalized events: 1 (from 4 raw)" in condensed

def test_normalize_logs_threat_scoring(sample_parsed_logs):
    # We can make this stronger now
    condensed = normalize_logs(sample_parsed_logs, threat_ports={8443: 10}, exclude_ports=set())  # ← add exclude_ports=set() to include all
    assert "Threat score total: 13" in condensed  # 3×1 (UDP) + 10 (TCP) = 13
    assert "(HIGH)" in condensed  # for 8443

def test_normalize_logs_threat_level():
    logs = [
        {'src_ip': '1.1.1.1', 'dst_port': 3389, 'proto': 'TCP'},
        {'src_ip': '2.2.2.2', 'dst_port': 80, 'proto': 'TCP'},
    ]
    condensed = normalize_logs(logs, exclude_ports=set())  # override exclusion
    assert "(HIGH)" in condensed  # 3389
    assert "(LOW)" in condensed   # 80

def test_normalize_logs_empty_input():
    condensed = normalize_logs([])
    assert "Total normalized events: 0 (from 0 raw)" in condensed
    assert "Threat score total: 0" in condensed
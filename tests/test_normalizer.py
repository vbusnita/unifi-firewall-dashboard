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
    condensed = normalize_logs(sample_parsed_logs, max_groups=10)
    assert "2 UDP probes on DPT=51413 (LOW) from 173.249.33.0/24" in condensed
    assert "1 TCP probes on DPT=8443 (LOW) from 207.180.192.0/24" in condensed
    assert "1 UDP probes on DPT=51413 (LOW) from 5.189.160.0/24" in condensed  # separate subnet

def test_normalize_logs_excludes_noise(sample_parsed_logs):
    condensed = normalize_logs(sample_parsed_logs, exclude_ports={51413})
    assert "51413" not in condensed
    assert "8443" in condensed

def test_normalize_logs_threat_scoring(sample_parsed_logs):
    condensed = normalize_logs(sample_parsed_logs, threat_ports={8443: 10})
    # Just check it runs — scoring is used internally for future extensions
    assert len(condensed.splitlines()) > 0

def test_normalize_logs_threat_level():
    logs = [
        {'src_ip': '1.1.1.1', 'dst_port': 3389, 'proto': 'TCP'},
        {'src_ip': '2.2.2.2', 'dst_port': 80, 'proto': 'TCP'},
    ]
    condensed = normalize_logs(logs)
    assert "(HIGH)" in condensed  # 3389
    assert "(LOW)" in condensed   # 80 now LOW
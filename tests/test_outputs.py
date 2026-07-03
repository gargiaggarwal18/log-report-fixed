import json
import re
from collections import Counter
from pathlib import Path

REPORT_PATH = Path("/app/report.json")
LOG_PATH = Path("/app/access.log")


def _load_report():
    assert REPORT_PATH.exists(), "no report.json found at /app/report.json"
    with open(REPORT_PATH) as f:
        return json.load(f)


def _compute_expected():
    """Independently recomputes ground truth from access.log for comparison."""
    paths, ips, total = Counter(), set(), 0
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            ips.add(line.split()[0])
            m = re.search(r'"(?:GET|POST|PUT|DELETE|HEAD|PATCH) (\S+) ', line)
            if m:
                paths[m.group(1)] += 1
    return {
        "total_requests": total,
        "unique_ips": len(ips),
        "top_path": paths.most_common(1)[0][0],
    }


def test_report_exists():
    """Verifies instruction.md criterion: agent must save a JSON summary to /app/report.json."""
    assert REPORT_PATH.exists(), "no report.json found"


def test_report_is_valid_json():
    """Verifies instruction.md criterion: output must be a JSON object."""
    with open(REPORT_PATH) as f:
        json.load(f)


def test_total_requests_correct():
    """Verifies instruction.md criterion: total_requests must equal the total number of log lines."""
    report = _load_report()
    expected = _compute_expected()
    assert report["total_requests"] == expected["total_requests"], (
        f"expected {expected['total_requests']}, got {report.get('total_requests')}"
    )


def test_unique_ips_correct():
    """Verifies instruction.md criterion: unique_ips must equal the count of distinct client IPs."""
    report = _load_report()
    expected = _compute_expected()
    assert report["unique_ips"] == expected["unique_ips"], (
        f"expected {expected['unique_ips']}, got {report.get('unique_ips')}"
    )


def test_top_path_correct():
    """Verifies instruction.md criterion: top_path must be the most frequently requested path."""
    report = _load_report()
    expected = _compute_expected()
    assert report["top_path"] == expected["top_path"], (
        f"expected {expected['top_path']}, got {report.get('top_path')}"
    )
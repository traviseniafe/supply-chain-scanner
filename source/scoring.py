from dataclasses import dataclass
from .osv_client import VulnerabilityFinding

@dataclass(frozen=True)
class RiskScore:
    score: int
    level: str
    vulnerability_count: int


def score_findings(findings: list[VulnerabilityFinding]) -> RiskScore:
    count = sum(len(item.vulnerabilities) for item in findings)
    score = min(count * 25, 100)

    if score == 0:
        level = "none"
    elif score < 50:
        level = "low"
    elif score < 75: 
        level = "medium"
    elif score < 100:
        level = "high"
    else:
        level = "critical"

    return RiskScore(score, level, count)
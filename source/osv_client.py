# Small client for querying the OSV vulnerability database.

from __future__ import annotations
from dataclasses import dataclass
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .parser import Dependency


OSV_QUERYBATCH_URL = "https://api.osv.dev/v1/querybatch"


@dataclass(frozen=True)
class VulnerabilityFinding:
    dependency: Dependency
    vulnerabilities: list[dict]


class OsvClientError(RuntimeError):
    """Raised when OSV cannot be reached or returns an invalid response."""


def lookup_vulnerabilities(
    dependencies: list[Dependency], *, timeout: float = 15.0
) -> list[VulnerabilityFinding]:
    """Look up exact PyPI versions in OSV, preserving input order.

    An empty dependency list returns immediately without making a request.
    OSV's querybatch response contains one result per submitted query.
    """
    if not dependencies:
        return []

    payload = {
        "queries": [
            {
                "package": {"name": dependency.name, "ecosystem": "PyPI"},
                "version": dependency.version,
            }
            for dependency in dependencies
        ]
    }
    request = Request(
        OSV_QUERYBATCH_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OsvClientError(f"OSV query failed: {exc}") from exc

    results = body.get("results") if isinstance(body, dict) else None
    if not isinstance(results, list) or len(results) != len(dependencies):
        raise OsvClientError("OSV returned an invalid querybatch response")

    findings = []
    for dependency, result in zip(dependencies, results):
        if not isinstance(result, dict):
            raise OsvClientError("OSV returned an invalid result entry")
        vulnerabilities = result.get("vulns", [])
        if not isinstance(vulnerabilities, list) or not all(
            isinstance(vulnerability, dict) for vulnerability in vulnerabilities
        ):
            raise OsvClientError("OSV returned invalid vulnerability data")
        findings.append(VulnerabilityFinding(dependency, vulnerabilities))
    return findings

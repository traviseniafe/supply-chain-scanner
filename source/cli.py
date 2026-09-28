import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from .osv_client import OsvClientError, lookup_vulnerabilities
from .parser import parse_requirements
from .sbom import write_cyclonedx_sbom
from .scoring import score_findings


def make_report(parsed, findings):
    return {
        "source": "OSV",
        "ecosystem": "PyPI",
        "risk": asdict(score_findings(findings)),
        "dependencies": [
            {
                "name": item.dependency.name,
                "version": item.dependency.version,
                "vulnerabilities": item.vulnerabilities,
            }
            for item in findings
        ],
        "skipped_lines": [asdict(line) for line in parsed.skipped],
    }


def print_table(report):
    risk = report["risk"]
    print(f"Risk: {risk['level']} ({risk['score']}/100)")
    print("Package                 Version       Vulnerabilities")
    print("-" * 62)

    for item in report["dependencies"]:
        ids = ", ".join(
            vulnerability.get("id", "Unknown ID")
            for vulnerability in item["vulnerabilities"]
        ) or "None found"

        print(f"{item['name']:<24} {item['version']:<13} {ids}")

    if report["skipped_lines"]:
        print(f"\nSkipped lines: {len(report['skipped_lines'])}")
        for line in report["skipped_lines"]:
            print(
                f"  Line {line['line_number']}: "
                f"{line['reason']} ({line['line'].strip()})"
            )


def main():
    command = argparse.ArgumentParser(
        description="Check pinned Python packages against OSV."
    )
    command.add_argument(
        "requirements",
        nargs="?",
        default="requirements.txt",
        help="Requirements file to scan",
    )
    command.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="How to show the report",
    )
    command.add_argument(
        "--output",
        help="Save the JSON report to a file",
    )
    command.add_argument(
        "--sbom",
        help="Save a CycloneDX inventory to a file",
    )
    args = command.parse_args()

    try:
        text = Path(args.requirements).read_text(encoding="utf-8")
    except OSError as error:
        print(f"Could not read requirements file: {error}", file=sys.stderr)
        return 2

    parsed = parse_requirements(text)

    try:
        findings = lookup_vulnerabilities(list(parsed))
    except OsvClientError as error:
        print(f"Could not check OSV: {error}", file=sys.stderr)
        return 2

    report = make_report(parsed, findings)

    if args.output:
        Path(args.output).write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
    elif args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print_table(report)

    if args.sbom:
        write_cyclonedx_sbom(list(parsed), args.sbom)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
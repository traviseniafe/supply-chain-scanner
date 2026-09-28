import json
import uuid

from .parser import Dependency


def create_cyclonedx_sbom(dependencies: list[Dependency]) -> dict:
    components = []

    for dependency in dependencies:
        purl = f"pkg:pypi/{dependency.name}@{dependency.version}"
        components.append({
            "type": "library",
            "name": dependency.name,
            "version": dependency.version,
            "purl": purl,
            "bom-ref": purl,
        })

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "components": components,
    }


def write_cyclonedx_sbom(dependencies: list[Dependency], path: str) -> None:
    with open(path, "w", encoding="utf-8") as output:
        json.dump(create_cyclonedx_sbom(dependencies), output, indent=2)
        output.write("\n")
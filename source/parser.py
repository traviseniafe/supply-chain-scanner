from dataclasses import dataclass

@dataclass(frozen=True)
class Dependency:
    name: str
    version: str

def parse_requirements(text: str) -> list[Dependency]:
    dependencies = []
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        if "==" not in line:
            continue
        name, version = line.split("==", 1)
        name = name.split("[", 1)[0].strip().lower().replace("_", "-")
        version = version.split(";", 1)[0].strip()
        dependencies.append(Dependency(name, version))
    return dependencies
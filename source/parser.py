from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Dependency:
    name: str
    version: str

@dataclass(frozen=True)
class SkippedLine:
    line_number: int
    line: str
    reason: str

class ParseResult(list[Dependency]):
    """Parsed dependencies with skipped input attached as metadata.

    It behaves like the original dependency list for callers that only need
    successfully parsed entries.
    """

    def __init__(self, dependencies: list[Dependency], skipped: list[SkippedLine]):
        super().__init__(dependencies)
        self.skipped = skipped

    @property
    def dependencies(self) -> list[Dependency]:
        return list(self)

_PINNED_REQUIREMENT = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^]]+\])?\s*==\s*([^\s;]+)(?:\s*;.*)?$")

def parse_requirements(text: str) -> ParseResult:
    dependencies = []
    skipped = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            if line.startswith("-"):
                skipped.append(SkippedLine(line_number, raw_line, "requirement options and includes are not followed"))
            continue
        match = _PINNED_REQUIREMENT.fullmatch(line)
        if not match:
            skipped.append(SkippedLine(line_number, raw_line, "not an exact package==version requirement"))
            continue
        name, version = match.groups()
        name = re.sub(r"[-_.]+", "-", name.lower())
        dependencies.append(Dependency(name, version))
    return ParseResult(dependencies, skipped)

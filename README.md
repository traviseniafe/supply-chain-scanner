# Supply Chain Scanner

A beginner-friendly Python tool that reads a list of Python packages, checks their exact versions against the public OSV vulnerability database, and can create a CycloneDX SBOM package inventory.

> **Status: early prototype (v0.1).** The main scan works, but the risk score is a simple starting point. See [Known limits](#known-limits).

## What does it do?

The scanner follows these steps:

```text
requirements file → read package names and versions → ask OSV → show results
                                                              └→ save an SBOM
```

- `source/parser.py` reads the requirements file and records lines it cannot use.
- `source/osv_client.py` asks OSV about each exact Python package version.
- `source/scoring.py` gives the results a simple score.
- `source/sbom.py` creates a CycloneDX package inventory.
- `source/cli.py` connects these parts so you can run them from the terminal.

## What is a requirements file?

A `requirements.txt` file is a plain text list of packages and versions. For example:

```text
requests==2.19.0
django==2.2.0
```

The `==` means “this exact version.” The scanner needs an exact version so it knows what to ask OSV about. A line like `requests>=2.0` allows many possible versions, so the scanner skips it and reports why.

The scanner reads the file you give it. It does **not** automatically find packages in another project, and it does **not** install the packages.

## Try the included demo

The demo file is `examples/demo-requirements.txt`. It contains old package versions chosen to demonstrate vulnerability results. They are examples, not recommended versions for a real application. You do not need to install them.

From the scanner’s main folder, run:

```bash
python -m source.cli examples/demo-requirements.txt
```

This prints a readable table in the terminal.

To print the vulnerability report as JSON and save a CycloneDX SBOM:

```bash
python -m source.cli examples/demo-requirements.txt --format json --sbom sbom.json
```

The JSON vulnerability report is printed in the terminal. The SBOM is saved as `sbom.json` in the current folder.

## Scan your own project

Use a `requirements.txt` file from the Python project you want to check. If it is in the scanner’s main folder, run:

```bash
python -m source.cli requirements.txt
```

If the file is somewhere else, give its path:

```bash
python -m source.cli path/to/your/requirements.txt
```

You can also ask for JSON output and save an SBOM:

```bash
python -m source.cli path/to/your/requirements.txt --format json --sbom sbom.json
```

If you do not provide a filename, the scanner looks for `requirements.txt` in the current folder.

## Set up and run

You need Python 3.10 or newer and an internet connection for the OSV lookup. The scanner uses Python’s standard library and does not need third-party packages to run.

Create and activate a virtual environment from the scanner’s main folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

```powershell
.venv\Scripts\activate
```

Then run the demo or scan your own requirements file using the commands above.

## Understand the results

For each package, the report shows its name, version, and vulnerability records returned by OSV. If OSV has no matching records for a package, the report says `None found`.

The parser also reports lines it skipped, including their line numbers and reasons. This makes it clear when a line was not checked.

### About the risk score

The current score adds 25 points for each OSV record, up to 100:

- 0 points: `none`
- 25 points: `low`
- 50 points: `medium`
- 75 points: `high`
- 100 points: `critical`

This is a simple prototype score. It is **not** an OSV severity rating and does not tell you whether an issue can be exploited in your project. OSV can return multiple records about the same underlying issue, so the score may count more records than distinct vulnerabilities.

## What is an SBOM?

SBOM means **Software Bill of Materials**. It is an inventory of the packages and versions checked by the scanner.

The saved `sbom.json` file uses the CycloneDX JSON format. It lists package names and versions; it is separate from the vulnerability report and does not contain the OSV findings.

## Known limits

- Checks Python packages in the PyPI ecosystem.
- Checks exact pinned versions such as `flask==3.0.0`.
- Reports unsupported or unpinned lines as skipped.
- Does not follow requirements-file includes such as `-r other-requirements.txt`.
- Does not resolve transitive dependencies (packages required by your packages).
- Does not scan source code, containers, or running systems.
- Does not determine whether a vulnerability can be exploited in your application.
- Does not install, upgrade, or fix packages.
- Uses a basic risk score that can count duplicate advisory records.

## Run the tests

Install pytest if needed:

```bash
python -m pip install pytest
```

Then run the tests from the scanner’s main folder:

```bash
python -m pytest
```

The current tests check the requirements parser. The OSV client, score, SBOM, and command-line flow still need their own automated tests.

## Roadmap

- [x] Read pinned Python requirements
- [x] Normalize package names
- [x] Report skipped lines
- [x] Look up exact package versions in OSV
- [x] Print a command-line report
- [x] Calculate a basic risk score
- [x] Export a CycloneDX JSON SBOM
- [ ] Add tests for the OSV client, scoring, SBOM, and command-line flow
- [ ] Improve scoring and avoid counting duplicate advisory records
- [ ] Add result caching
- [ ] Add a GitHub Actions workflow to run tests
- [ ] Support other ecosystems, such as npm
- [ ] Resolve transitive dependencies
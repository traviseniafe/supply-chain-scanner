from source.parser import Dependency, parse_requirements


def test_pinned_package_is_parsed():
    assert parse_requirements("requests==2.19.0") == [Dependency("requests", "2.19.0")]


def test_comments_and_blank_lines_are_ignored():
    text = "# a comment\n\nflask==2.0.0  # inline comment\n"
    assert parse_requirements(text) == [Dependency("flask", "2.0.0")]


def test_unpinned_packages_are_skipped():
    assert parse_requirements("django>=3.0") == []


def test_extras_and_markers_are_removed():
    text = 'requests[security]==2.19.0 ; python_version < "3.9"'
    assert parse_requirements(text) == [Dependency("requests", "2.19.0")]
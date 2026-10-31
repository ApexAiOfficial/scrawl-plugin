"""Shared paths and parsers for the plugin's tests."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "scrawl"
SKILLS_DIR = PLUGIN / "skills"
SKILLS = sorted(path.parent.name for path in SKILLS_DIR.glob("*/SKILL.md"))
EXPECTED_SKILLS = ["ask", "crawl", "datasets", "downloads", "extract", "map", "scrape", "scrawl", "setup"]
CONTRACT = ROOT / "contracts" / "mcp_tools.json"

#: Every Markdown file a user or an agent reads: the skills and their references, the READMEs and the docs.
SKILL_FILES = sorted(SKILLS_DIR.glob("**/*.md"))
DOC_FILES = sorted([ROOT / "README.md", PLUGIN / "README.md", *(ROOT / "docs").glob("*.md")])


def load_json(path: Path) -> dict:
    """A JSON file as a dict."""
    return json.loads(path.read_text(encoding="utf-8"))


def frontmatter(path: Path) -> tuple[dict[str, str], str]:
    """(the ``key: value`` front matter of a Markdown file, its body)."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n(.*)\Z", text, re.S)
    assert match, f"{path} has no front matter"
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        assert sep and re.fullmatch(r"[a-z][a-z0-9_-]*", key), f"{path}: unexpected front matter line {line!r}"
        meta[key] = value.strip()
    return meta, match.group(2)


def without_code_blocks(text: str) -> str:
    """TEXT with fenced code blocks removed."""
    return re.sub(r"^```.*?^```[ \t]*$", "", text, flags=re.S | re.M)


def tools() -> dict[str, dict]:
    """The vendored MCP tool contract, by tool name."""
    return {tool["name"]: tool for tool in json.loads(CONTRACT.read_text(encoding="utf-8"))}


@pytest.fixture(scope="session")
def scrawl_cli():
    """The real ``scrawl.cli`` module. Required in CI (SCRAWL_PLUGIN_REQUIRE_CLI=1), skipped elsewhere if absent."""
    try:
        import scrawl.cli as cli
    except ModuleNotFoundError:
        if os.environ.get("SCRAWL_PLUGIN_REQUIRE_CLI") == "1":
            raise
        pytest.skip("the scrawl CLI is not installed (pip install the Scrawl Python SDK)")
    return cli

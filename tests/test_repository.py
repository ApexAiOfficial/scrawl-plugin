"""Publishing hygiene: nothing private, reserved example hosts only, and CI that stays on hosted runners."""

from __future__ import annotations

import re
import subprocess

import pytest
from conftest import ROOT

#: Hosts a published file may link to: documentation, the project's own homes, and reserved example names.
LINK_HOSTS = {
    "github.com", "json.schemastore.org", "keepachangelog.com", "semver.org", "www.apache.org",
    "code.claude.com", "claude.com", "claude.ai", "developers.openai.com", "platform.openai.com",
    "learn.chatgpt.com", "chatgpt.com", "help.openai.com", "modelcontextprotocol.io", "agentskills.io",
    "apexaiofficial.com",
}
RESERVED = re.compile(r"^(?:[a-z0-9-]+\.)*(?:example|test|localhost)$|^127\.0\.0\.1$|^\[::1\]$")


def _published_files() -> list:
    try:
        listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):           # not a git checkout: every regular file
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
    return [ROOT / name for name in listed if (ROOT / name).is_file()]


FILES = [p for p in _published_files() if p.suffix in {".md", ".json", ".py", ".yml", ".yaml", ".svg", ""}
         and p.name not in ("mcp_tools.json", "LICENSE")]


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_nothing_private(path) -> None:
    text = path.read_text(encoding="utf-8")
    patterns = {
        "home directory": r"/home/[a-z]|/Users/[A-Za-z]|[A-Z]:\\Users\\",
        "internal decision id": r"\b(?:OD|ADR|BR)-\d|\bK\d{1,2}\b",
        "backend package path": r"apexai_scrapy_" + r"bot",
        "private address": r"\badmin@",
    }
    for label, pattern in patterns.items():
        match = re.search(pattern, text)
        assert not match, f"{path.relative_to(ROOT)}: {label}: {match.group(0)!r}"


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_only_reserved_or_documentation_hosts(path) -> None:
    text = path.read_text(encoding="utf-8")
    for netloc in re.findall(r"https?://([^/\s\"'`)<>\]]+(?:\])?)", text):
        host = re.sub(r":\d+$", "", netloc).lower()
        if "{" in host or "$" in host or host in ("www.w3.org",):        # placeholders; the SVG namespace
            continue
        assert host in LINK_HOSTS or RESERVED.match(host), f"{path.relative_to(ROOT)}: {netloc}"


def test_ci_runs_on_github_hosted_runners_only() -> None:
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        text = workflow.read_text(encoding="utf-8")
        runners = re.findall(r"runs-on:\s*(.+)", text)
        assert runners and set(runners) == {"ubuntu-latest"}, f"{workflow.name}: {runners}"
        assert "permissions:\n  contents: read" in text, workflow.name


def test_no_secrets_or_local_state_are_tracked() -> None:
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in (".env", ".venv/", "__pycache__/", ".DS_Store"):
        assert pattern in ignored
    placeholder = re.compile(r"^(?:\$\{[^}]+\}|<[^>]+>|\.\.\.|…|\$[A-Z_]+|\"\$[A-Z_]+\")$")
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"\bsk_(?:live|test)_[A-Za-z0-9]{8,}", text), path
        for value in re.findall(r"Bearer ([^\s\"'`]+)", text):     # a literal token, not a placeholder
            literal = len(value) >= 12 and re.fullmatch(r"[A-Za-z0-9._~+/=-]+", value)
            assert not literal or placeholder.match(value), f"{path.name}: Bearer {value}"
        for value in re.findall(r"\bSCRAWL_(?:AI_)?API_KEY=([A-Za-z0-9._~+/=-]{8,})", text):
            assert value in ("probe-key", "scrawl-ci-probe-key"), f"{path.name}: SCRAWL_API_KEY={value}"
        for run in re.findall(r"[A-Za-z0-9_\-]{40,}", text):
            assert not re.fullmatch(r"(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z0-9_\-]+", run) or "_" in run.strip("_"), (
                f"{path.name}: a long random-looking string")



@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_the_cli_is_never_installed_from_an_unowned_package_name(path) -> None:
    """``scrawl`` on PyPI is an unrelated project and ``scrawl-sdk`` is not published there yet."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"\bpipx? install (?:-\S+ )*[\"']?scrawl(?:-sdk)?(?:[\"'\s`]|$)", text, re.M)
    assert not match, f"{path.relative_to(ROOT)}: {match.group(0)!r}"

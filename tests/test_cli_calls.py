"""Every ``scrawl ...`` command the skills and docs show parses with the real CLI, and every exit code they
promise for an error code is the one the real CLI returns."""

from __future__ import annotations

import contextlib
import io
import re
import shlex

import pytest
from conftest import DOC_FILES, ROOT, SKILL_FILES, SKILLS_DIR

FILES = [*SKILL_FILES, *DOC_FILES]
ERRORS_MD = SKILLS_DIR / "scrawl" / "references" / "errors.md"


def _commands(text: str) -> list[str]:
    """``scrawl`` commands in fenced bash blocks and in inline code (comments, redirects and pipes stripped)."""
    found: list[str] = []
    in_bash = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_bash = line.strip() in ("```bash", "```sh", "```shell")
            continue
        if in_bash:
            command = line.split(" #", 1)[0].strip()
            for part in re.split(r"\s*(?:&&|\|\||;|\|)\s*", command):
                part = part.split(" < ", 1)[0].split(" > ", 1)[0].strip()
                if part.startswith("scrawl "):
                    found.append(part)
    for span in re.findall(r"(?<!`)`([^`\n]+)`(?!`)", text):
        if span.startswith("scrawl "):
            found.append(span)
    return found


COMMANDS = [(path, command) for path in FILES for command in _commands(path.read_text(encoding="utf-8"))]


def test_the_skills_show_the_cli() -> None:
    skill_commands = [c for p, c in COMMANDS if p in SKILL_FILES]
    assert len(skill_commands) >= 50
    used = {shlex.split(c)[1 if not c.startswith("scrawl --json") else 2] for c in skill_commands
            if not c.startswith("scrawl --version")}
    for sub in ("scrape", "result", "map", "batch", "batch-status", "extract", "ask", "crawl", "job", "jobs",
                "cancel", "artifacts", "datasets", "search", "document", "ai", "assets", "assets-quote",
                "assets-result", "balance", "doctor"):
        assert sub in used, sub


def _names_a_command(cli, argv: list[str]) -> bool:
    """ARGV is only (sub)command names, such as ``ai providers``, and they exist: prose naming a command."""
    if not argv or not all(re.fullmatch(r"[a-z]+(?:-[a-z]+)*", word) for word in argv):
        return False
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            cli.build_parser().parse_args([*argv, "--help"])
    except SystemExit as exc:
        return exc.code == 0
    return False


@pytest.mark.parametrize(("path", "command"), COMMANDS,
                         ids=[f"{p.relative_to(ROOT)}:{c}" for p, c in COMMANDS])
def test_every_command_parses(scrawl_cli, path, command: str) -> None:
    argv = shlex.split(command)[1:]
    try:
        scrawl_cli.build_parser().parse_args(argv)
    except SystemExit as exc:                     # --version exits 0; anything else is a usage error
        assert exc.code == 0 or _names_a_command(scrawl_cli, argv), (
            f"{path.relative_to(ROOT)}: `{command}` does not parse")


def test_a_command_name_must_exist(scrawl_cli) -> None:
    assert _names_a_command(scrawl_cli, ["ai", "providers"])
    assert _names_a_command(scrawl_cli, ["datasets", "extract"])
    assert not _names_a_command(scrawl_cli, ["jobz"])
    assert not _names_a_command(scrawl_cli, ["artifacts", "download", "job_123"])


# -- exit codes -----------------------------------------------------------------------------------------

def _error_table() -> dict[str, tuple[int | None, int]]:
    """code -> (HTTP status or None, CLI exit) from the API code table in references/errors.md."""
    table: dict[str, tuple[int | None, int]] = {}
    in_table = False
    for line in ERRORS_MD.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Code | HTTP | CLI exit"):
            in_table = True
            continue
        if in_table and not line.startswith("|"):
            break
        if in_table and not line.startswith("| ---"):
            codes, status, exit_code = (cell.strip() for cell in line.strip("|").split("|")[:3])
            for code in re.findall(r"`([a-z_]+)`", codes):
                table[code] = (int(status) if status.isdigit() else None, int(exit_code))
    return table


ERROR_TABLE = _error_table()


class _FailingClient:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def credit_balance(self):
        raise self.exc


def test_the_error_table_is_complete() -> None:
    for code in ("unauthorized", "forbidden", "account_not_active", "insufficient_credits", "not_found",
                 "invalid_request", "rate_limited", "too_many_active_jobs", "egress_required", "budget_exceeded",
                 "browser_unavailable", "ai_quota", "render_not_supported"):
        assert code in ERROR_TABLE, code


@pytest.mark.parametrize("code", sorted(ERROR_TABLE))
def test_the_error_table_matches_the_real_cli(scrawl_cli, capsys, code: str) -> None:
    from scrawl import ScrawlError
    from scrawl._errors import error_for

    status, documented_exit = ERROR_TABLE[code]
    body = {"error": {"code": code, "message": "refused"}}
    exc = (error_for(status, body, request_id=None, retry_after=None) if status is not None
           else ScrawlError("refused", code=code))
    assert exc.code == code
    assert scrawl_cli.main(["balance"], client=_FailingClient(exc)) == documented_exit
    assert f"[{code}]" in capsys.readouterr().err


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_every_promised_exit_code_is_right(path) -> None:
    """A line that names error codes and exactly one ``exit N`` must give each code its real exit code."""
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        exits = set(re.findall(r"\bexit (\d)\b", line))
        codes = [c for c in re.findall(r"`([a-z_]+)`", line) if c in ERROR_TABLE]
        if len(exits) != 1 or not codes or path == ERRORS_MD:
            continue
        stated = int(exits.pop())
        for code in codes:
            assert ERROR_TABLE[code][1] == stated, (
                f"{path.name}:{number}: `{code}` exits {ERROR_TABLE[code][1]}, not {stated}")


def test_a_rate_limit_is_never_called_exit_3() -> None:
    """The earlier plugin said 429 too_many_active_jobs exits 3; the CLI returns 5."""
    for path in FILES:
        for line in path.read_text(encoding="utf-8").splitlines():
            if re.search(r"429|rate_limited|too_many_active_jobs", line):
                assert not re.search(r"\bexit(?: code)? 3\b|\bexits? with 3\b", line), f"{path.name}: {line}"


# -- waits: a host cuts off long commands, and a scrawl command cut off while waiting never prints its job ID ----

MAX_WAIT = 60


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_wait_outlasts_a_host_command_timeout(path) -> None:
    """Every ``--wait N`` the skills and docs show, in a command or in prose, is at most 60 seconds."""
    for value in re.findall(r"--wait[ =](\d+)", path.read_text(encoding="utf-8")):
        assert int(value) <= MAX_WAIT, f"{path.relative_to(ROOT)}: --wait {value}"


@pytest.mark.parametrize(("path", "command"), COMMANDS,
                         ids=[f"{p.relative_to(ROOT)}:{c}" for p, c in COMMANDS])
def test_no_command_relies_on_a_long_default_wait(scrawl_cli, path, command: str) -> None:
    """``scrawl batch`` and ``scrawl assets`` wait 300 seconds unless told otherwise: the real parser decides."""
    try:
        args = scrawl_cli.build_parser().parse_args(shlex.split(command)[1:])
    except SystemExit:                           # --version; parsing itself is checked above
        return
    if hasattr(args, "wait"):
        assert args.wait <= MAX_WAIT, f"{path.relative_to(ROOT)}: `{command}` waits {args.wait} seconds"


def test_the_long_default_waits_are_still_there(scrawl_cli) -> None:
    """If the CLI ever shortens these defaults, the explicit --wait in the skills can be revisited."""
    parser = scrawl_cli.build_parser()
    assert parser.parse_args(["batch", "https://shop.example"]).wait > MAX_WAIT
    assert parser.parse_args(["assets", "https://shop.example"]).wait > MAX_WAIT


def test_every_ai_profile_example_names_a_model(scrawl_cli) -> None:
    """The server has a default model only for some providers; a profile without one is refused."""
    examples = [c for _, c in COMMANDS if c.startswith("scrawl ai providers set ")]
    assert examples
    for command in examples:
        args = scrawl_cli.build_parser().parse_args(shlex.split(command)[1:])
        assert args.model or args.provider == "deepseek", command

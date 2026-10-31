"""Every MCP tool, and every argument, that a skill names exists in Scrawl's published MCP tool contract.

Skills write a tool call as ``tool_name(arg, arg)`` with argument names only. A name in an "MCP tool" table
column, or any ``apex_scrapy_*`` word anywhere, must be a contract tool; a call's arguments must be that tool's
input properties and must include every required one.
"""

from __future__ import annotations

import hashlib
import json
import re

import pytest
from conftest import CONTRACT, DOC_FILES, ROOT, SKILL_FILES, load_json, tools

TOOLS = tools()
FILES = [*SKILL_FILES, *DOC_FILES]
CALL = re.compile(r"`([a-z_][a-z0-9_]*)\(([^`()]*)\)`")
#: A tool name anywhere, also inside a host's prefixed name such as ``mcp__plugin_scrawl_scrawl__apex_scrapy_x``.
TOOL_WORD = re.compile(r"(?<![a-z0-9])apex_scrapy_[a-z0-9_]+")


def _calls(text: str) -> list[tuple[str, list[str]]]:
    calls = []
    for name, args in CALL.findall(text):
        if name in TOOLS or name.startswith("apex_scrapy_"):
            calls.append((name, [arg.strip() for arg in args.split(",") if arg.strip()]))
    return calls


def _mcp_column_names(text: str) -> list[str]:
    """Backticked names in the "MCP tool" column of every Markdown table."""
    names: list[str] = []
    column = None
    for line in text.splitlines():
        if not line.startswith("|"):
            column = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if column is None:
            column = next((i for i, cell in enumerate(cells) if cell.lower() == "mcp tool"), -1)
            continue
        if column >= 0 and column < len(cells) and not set(cells[column]) <= set("-: "):
            cell = cells[column]                  # a call anywhere, or a bare name that opens the cell
            names += re.findall(r"`([a-z_][a-z0-9_]*)\(", cell)
            names += re.findall(r"^`([a-z_][a-z0-9_]*)`", cell)
    return names


def test_the_vendored_contract_matches_its_manifest() -> None:
    manifest = load_json(ROOT / "contracts" / "MANIFEST.json")
    data = CONTRACT.read_bytes()
    assert manifest["files"]["mcp_tools.json"] == {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    assert manifest["source"]["repository"] == "https://github.com/ApexAiOfficial/scrawl-sdk"
    assert len(json.loads(data)) == len(TOOLS) > 0


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_every_named_tool_exists(path) -> None:
    text = path.read_text(encoding="utf-8")
    named = set(TOOL_WORD.findall(text)) | set(_mcp_column_names(text))
    named |= {name for name, _ in _calls(text)}
    unknown = sorted(name for name in named if name not in TOOLS)
    assert not unknown, f"{path.name} names tools the contract does not have: {unknown}"


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_every_call_uses_real_arguments_and_all_required_ones(path) -> None:
    for name, args in _calls(path.read_text(encoding="utf-8")):
        schema = TOOLS[name]["inputSchema"]
        properties = set(schema.get("properties", {}))
        for arg in args:
            assert re.fullmatch(r"[a-z_][a-z0-9_]*", arg), f"{path.name}: {name}({arg}): names only, no values"
            assert arg in properties, f"{path.name}: {name} has no argument {arg!r} (has {sorted(properties)})"
        missing = set(schema.get("required", [])) - set(args)
        assert not missing, f"{path.name}: {name}(...) leaves out required {sorted(missing)}"


def test_the_skills_cover_the_customer_tools() -> None:
    """Every tool a customer needs is reachable from some skill; operator-only tools may stay unnamed."""
    text = "\n".join(path.read_text(encoding="utf-8") for path in SKILL_FILES)
    named = set(TOOL_WORD.findall(text)) | {name for name, _ in _calls(text)}
    operator_only = {"apex_scrapy_check_project", "apex_scrapy_list_capabilities", "apex_scrapy_version"}
    assert set(TOOLS) - operator_only <= named, sorted(set(TOOLS) - operator_only - named)


def test_the_parser_finds_what_it_should() -> None:
    sample = ("| Step | MCP tool | CLI |\n| --- | --- | --- |\n"
              "| a | `apex_scrapy_get_job(job_id, wait_seconds)` | `scrawl job job_1` |\n"
              "| b | `search(query)` | none |\n| c | `apex_scrapy_status` with view `skipped` | none |\n"
              "\nprose `fetch(id)` and `len(x)`")
    assert _mcp_column_names(sample) == ["apex_scrapy_get_job", "search", "apex_scrapy_status"]
    assert _calls(sample) == [("apex_scrapy_get_job", ["job_id", "wait_seconds"]), ("search", ["query"]),
                              ("fetch", ["id"])]
    assert TOOL_WORD.findall("`mcp__plugin_scrawl_scrawl__apex_scrapy_scrape_url` and `apex_scrapy_*`") == [
        "apex_scrapy_scrape_url"]


#: Result fields the skills tell the agent to read, by tool. A contract update that drops one fails here.
RESULT_FIELDS = {
    "apex_scrapy_scrape_url": ["status", "job_id", "title", "final_url", "truncated", "data", "error_code", "engine"],
    "apex_scrapy_scrape_result": ["status", "job_id"],
    "apex_scrapy_map_url": ["status", "links", "sources", "truncated", "warnings", "job_ids", "error"],
    "apex_scrapy_batch_scrape": ["batch_id"],
    "apex_scrapy_start_crawl": ["job_id", "dataset_id", "dataset_version_id"],
    "apex_scrapy_get_job": ["status"],
    "apex_scrapy_extract": ["data", "provider", "model", "input_tokens", "output_tokens", "warnings", "repaired",
                            "truncated"],
    "apex_scrapy_extract_dataset": ["job_id", "target_dataset_id"],
    "apex_scrapy_ai_status": ["enabled", "configured"],
    "apex_scrapy_ask": ["answer", "answerable", "citations", "sources_considered", "provider", "model",
                        "input_tokens", "output_tokens", "tag", "title", "url", "document_id", "dataset_id"],
    "apex_scrapy_query_dataset_version": ["records", "next_cursor", "record_id", "title", "url", "text", "record",
                                          "provenance"],
    "apex_scrapy_diff_dataset_versions": ["entries", "totals", "next_cursor", "record_id", "change"],
    "apex_scrapy_asset_result": ["status", "counts", "billing", "partial", "next_cursor", "assets"],
    "search": ["results", "id", "title", "text", "url"],
    "fetch": ["id", "text", "url"],
}


@pytest.mark.parametrize("tool", sorted(RESULT_FIELDS))
def test_the_result_fields_the_skills_read_exist(tool: str) -> None:
    schema = TOOLS[tool]["outputSchema"]
    properties = set(schema.get("properties", {}))
    for definition in schema.get("$defs", {}).values():
        properties |= set(definition.get("properties", {}))
    missing = [field for field in RESULT_FIELDS[tool] if field not in properties]
    assert not missing, f"{tool} no longer returns {missing}"

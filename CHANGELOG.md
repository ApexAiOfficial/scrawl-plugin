# Changelog

All notable changes to the Scrawl plugin. The format follows [Keep a Changelog](https://keepachangelog.com/),
and versions follow [Semantic Versioning](https://semver.org/). The version in
`plugins/scrawl/.claude-plugin/plugin.json` and `plugins/scrawl/.codex-plugin/plugin.json` is the plugin's
version in both hosts.

## 0.1.0 (2026-10-31)

First public version.

### Added
- One repository serving Claude Code and OpenAI Codex: a marketplace for each host (`apexai-scrawl`) and the
  `scrawl` plugin with a manifest for each.
- MCP connection to Scrawl's MCP endpoint over Streamable HTTP with a per-request bearer API key. Claude Code
  takes the URL and key from the plugin's settings (`api_key` sensitive and required; `mcp_url` and
  `base_url` with loopback defaults); Codex reads the key from `SCRAWL_API_KEY`.
- Nine skills shared by both hosts: `scrawl` (overview, cost, limits, untrusted content, error codes),
  `setup`, `scrape`, `map`, `crawl`, `extract`, `ask`, `datasets` and `downloads`. Each drives the MCP tools
  or the `scrawl` CLI and says which it prefers.
- The vendored MCP tool contract (`contracts/mcp_tools.json`) and tests that check every MCP tool and
  argument the skills name against it, and every `scrawl` command against the real CLI parser.
- CI on GitHub-hosted runners: strict manifest validation with a pinned Claude Code, an install check with
  a pinned Codex CLI, and the contract tests.
- The `scrawl` CLI the skills and CI use is pinned to the SDK's `py-v0.1.0` release.
- Codex guide: scripted runs (`codex exec` needs the Scrawl tools approved for the run) and a warning that
  `codex mcp add` and `codex mcp remove` rewrite the whole `config.toml`.

### Changed (from the earlier Claude Code plugin)
- The `/scrawl:scrape` and `/scrawl:map` commands are now skills of the same names, so they also work in
  Codex.
- Exit-code guidance corrected: a 429 (`rate_limited`, `too_many_active_jobs`) ends the CLI with exit 5, not 3.

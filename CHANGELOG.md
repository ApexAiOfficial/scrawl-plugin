# Changelog

All notable changes to the Scrawl plugin. The format follows [Keep a Changelog](https://keepachangelog.com/),
and versions follow [Semantic Versioning](https://semver.org/). The version in
`plugins/scrawl/.claude-plugin/plugin.json` and `plugins/scrawl/.codex-plugin/plugin.json` is the plugin's
version in both hosts.

## 0.1.4 (2026-11-16)

Matches the scrawl-sdk release it works with (Python and TypeScript 0.1.4).

### Changed
- The crawl skill mentions a job's `warnings`: a job read by ID now carries notes about a run that still
  succeeded, for example a crawl that made zero requests. The vendored MCP contract includes the field on
  `apex_scrapy_get_job`.
- The map skill handles a blocked start page: `outcome` `target_blocked` with its reason and hint. `scrawl map`
  exits 1 and says why, and the skill tells the user instead of repeating the map.
- The error reference states the CLI's retry rule: a Retry-After of 60 s or less is retried (in seconds or as an
  HTTP date), and a longer one is reported at once, never retried early. This now covers gateway errors too.
- The CI validates the skills against scrawl-sdk `py-v0.1.4`.

## 0.1.3 (2026-11-16)

The plugin skips 0.1.2 so that its version matches the scrawl-sdk release it works with (Python and TypeScript
0.1.3).

### Added
- The setup skill covers a proxy pool (`scrawl proxy pool add|test|mode|list`, with the URL only from
  `SCRAWL_PROXY_URL`, `--url-env` or the user's own terminal), the free `scrawl proxy health` report, and the
  account's API keys (`scrawl keys list|revoke`; keys are made in Telegram). The overview skill routes to them.
- The charging rule, stated before the first job: a job is charged once it runs through the user's proxy, also when
  the target blocks it; refunds are automatic and cover only Scrawl's own failures (a job that never started, and a
  scrape whose `outcome` is `pipeline_failed`).
- The scrape skill reads a result's `outcome`, `block_reason`, `retry_after_s` and `hint`, and a batch's
  `outcomes` counts.

### Changed
- `rate_limited` is per API key on ApexAPI and per account on MCP; the CLI retries a wait of up to 60 s itself
  and reports a longer one with its Retry-After.
- The vendored MCP tool contract is re-synced from scrawl-sdk 0.1.3 (contract digest `sha256:050c2402…`).
- The setup skill installs the CLI from `py-v0.1.3`, and CI checks every command in the skills against the CLI
  from scrawl-sdk `py-v0.1.3` (commit `0885f66`).

## 0.1.1 (2026-11-14)

### Added
- The setup skill's step 4: the user's own proxy, which every Scrawl job needs before anything is fetched
  (`scrawl proxy show|set|test`, with the URL from `SCRAWL_PROXY_URL` or stdin, never the conversation or a
  command line). The overview skill routes proxy work to it, and `egress_required` now points there.

### Changed
- The vendored MCP tool contract is re-synced from scrawl-sdk 0.1.1 (contract digest `sha256:417e9fce…`).
- The setup skill installs the CLI from `py-v0.1.1` (which has `scrawl proxy`), and says that `anthropic`, like
  `deepseek`, has a server default model.
- CI checks every command in the skills against the `scrawl` CLI from scrawl-sdk `py-v0.1.1` (commit `60a6c74`),
  so the new `scrawl proxy` commands are parsed, not skipped.

## Earlier unreleased changes, shipped in 0.1.1

### Changed
- The vendored MCP tool contract is re-synced from scrawl-sdk (contract digest `sha256:36eed387…`): Scrawl's tool
  descriptions now call the deployment ApexAi runs for one customer a "dedicated deployment". Wording only: no
  tool, argument or skill changes.

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

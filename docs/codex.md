# Scrawl in OpenAI Codex

Verified with Codex CLI 0.157.1: install, MCP registration, and delivery of the key to a stand-in MCP server.
The IDE extension and the Codex app share the Codex configuration, so they should load the same plugin; they
are not tested here.

## Install

```bash
codex plugin marketplace add ApexAiOfficial/scrawl-plugin        # --ref <tag> pins a release
codex plugin add scrawl@apexai-scrawl
```

Codex reads this repository's `.agents/plugins/marketplace.json` (marketplace `apexai-scrawl`) and the
plugin's `.codex-plugin/plugin.json`, which points at the shared `skills/` and at `.codex-mcp.json` for the MCP
server. It ignores the Claude Code files.

## Give Codex your key

The plugin's MCP server sends the key from the `SCRAWL_API_KEY` environment variable as a bearer token.
Export it in the environment Codex starts from (your shell profile, or the environment of the IDE or app),
then start Codex:

```bash
export SCRAWL_API_KEY=...            # your Scrawl API key; keep it out of shared files and transcripts
codex
```

`codex mcp list` shows the server with `Bearer token` auth.

## Point it at another endpoint

The plugin connects to `http://127.0.0.1:8000/mcp`, a loopback address (Scrawl's MCP server currently accepts
only local connections). Codex does not expand variables or plugin settings in a plugin's MCP URL, so to use
the MCP endpoint ApexAi provides for your account, define an MCP server named `scrawl` in your own
configuration; it replaces the plugin's entry of the same name:

```bash
codex mcp add scrawl --url https://scrawl.example/mcp --bearer-token-env-var SCRAWL_API_KEY
codex mcp list --json        # "url": "https://scrawl.example/mcp", "auth_status": "bearer_token"
```

This writes to `~/.codex/config.toml`:

```toml
[mcp_servers.scrawl]
url = "https://scrawl.example/mcp"
bearer_token_env_var = "SCRAWL_API_KEY"
```

Keep `bearer_token_env_var` in the override: your entry replaces the plugin's entirely, so without it no key
is sent. `codex mcp remove scrawl` returns to the plugin's default. A project's `.codex/config.toml` can carry
the same entry, but Codex applies project configuration only in projects you have marked as trusted.

`codex mcp add` and `codex mcp remove` rewrite the whole `config.toml`, not just the `scrawl` table. In our
test with Codex 0.157.1, an add followed by a remove also dropped the `args` of another MCP server in the same
file. Copy `config.toml` before using them, or edit the `[mcp_servers.scrawl]` table by hand instead.

## Switch the MCP server off

While `SCRAWL_API_KEY` is set, Codex sends it to the plugin's MCP URL every time it starts, whatever answers
there. If no Scrawl MCP endpoint answers at that URL (for example, you export `SCRAWL_API_KEY` only for the
CLI), switch the entry off in `config.toml` in your Codex home:

```toml
[mcp_servers.scrawl]
url = "http://127.0.0.1:8000/mcp"
enabled = false
```

Codex 0.157.1 then lists the server as disabled and sends nothing to it; the skills keep working through the
CLI. Remove the entry to switch the server back on.

## The CLI route

The skills use the `scrawl` CLI for downloads, the setup check, AI provider profiles, and whenever Scrawl's MCP
endpoint is not reachable. It reads `SCRAWL_BASE_URL` and `SCRAWL_API_KEY` from the same environment:

```bash
export SCRAWL_BASE_URL=https://scrawl.example   # the ApexAPI endpoint ApexAi provides for your account
scrawl doctor
```

Codex runs commands in its sandbox; allow network access for `scrawl` commands when Codex asks.

## Scripted runs (`codex exec`)

`codex exec` has nobody to approve an MCP tool call. In our tests with Codex 0.157.1, a run that had not
pre-approved the Scrawl tools made no call that reached the server. Approve them for that run only:

```bash
codex exec -c mcp_servers.scrawl.default_tools_approval_mode="approve" "Scrape https://docs.example/ with Scrawl"
```

Every Scrawl tool then runs without asking, under the key in `SCRAWL_API_KEY`, so give a scripted run a key
with only the scopes it needs. The same setting in `config.toml` applies to every session, interactive ones
included; prefer the per-run flag.

## Skills

Codex lists them as `scrawl:scrawl`, `scrawl:setup`, `scrawl:scrape`, `scrawl:map`, `scrawl:crawl`,
`scrawl:extract`, `scrawl:ask`, `scrawl:datasets` and `scrawl:downloads`, and picks them by their
descriptions. One skill line is unique to Claude Code: the setup skill shows a `${user_config.base_url}`
placeholder that Codex leaves unfilled and that the skill tells the agent to ignore.

## Update and remove

```bash
codex plugin marketplace upgrade apexai-scrawl
codex plugin remove scrawl@apexai-scrawl
codex plugin marketplace remove apexai-scrawl
```

## What Codex does not use

Codex does not run plugin hooks (this plugin has none), does not read Claude Code's `userConfig`, and drops the
Claude `headers` field from an MCP entry: that is why Codex has its own `.codex-mcp.json`.

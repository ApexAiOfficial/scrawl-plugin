# Security

## Reporting a vulnerability

Please report security problems privately, through GitHub's
[private vulnerability reporting](https://github.com/ApexAiOfficial/scrawl-plugin/security/advisories/new) for
this repository, or by email to support@apexaiofficial.com. Do not open a public issue for a vulnerability.

Include what you found, how to reproduce it, the plugin version and the host (Claude Code or Codex, with its
version). We aim to acknowledge reports within a few days.

## What the plugin promises

- **Your API key goes only to your MCP URL.** In Claude Code it is a `sensitive` plugin setting: entered in a
  masked field, kept in Claude Code's secure storage rather than `settings.json` (on Linux, Claude Code keeps
  it in a `.credentials.json` file readable only by your user), and substituted only into the
  `Authorization` header of the MCP server you configured. The plugin never reads a credential from your
  environment for Claude Code. In Codex, the host reads it from the `SCRAWL_API_KEY` variable you set and
  sends it as a bearer token to the configured MCP URL every time Codex starts; switch the entry off if no
  Scrawl MCP server runs there ([docs/codex.md](docs/codex.md)).
- **Whatever answers at that URL receives the key.** The default, `http://127.0.0.1:8000/mcp`, assumes your
  Scrawl MCP server listens on this machine's port 8000. If another program may use that port, set the MCP URL
  explicitly; the setup skill asks you to confirm the account that `apex_scrapy_status` reports. Neither host
  refuses a plain `http://` URL to another machine, and Claude Code does not warn about one: use `https://`
  for any host but this machine (the setup skill checks the configured URL in Claude Code).
- **No code runs from this plugin.** It ships skills (Markdown), manifests and MCP connection settings: no
  hooks, no executables, no scripts, no network code, no telemetry.
- **Scraped content is untrusted.** Every skill tells the agent to treat page text, extracted values, dataset
  records, answers and file names as data, never as instructions, and not to let them choose URLs, commands,
  files or settings. Downloaded files are never to be run.
- **Keys stay out of the conversation.** The skills never ask for a key in chat, never put one on a command
  line and never print one. The `scrawl` CLI reads its key only from the environment.
- **Changes that matter are confirmed.** Billable asset jobs are quoted first; rolling back a dataset,
  quarantining records and cancelling jobs need the user's agreement.

## Scope

This repository covers the plugin: its manifests, MCP configuration and skills. The `scrawl` CLI and SDKs live
in [scrawl-sdk](https://github.com/ApexAiOfficial/scrawl-sdk). Report problems with a Scrawl server to its
operator.

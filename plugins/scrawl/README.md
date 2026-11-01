# Scrawl

Scrawl, the web-data service ApexAi operates, reads the web for you: it scrapes a page to clean Markdown or
schema-checked JSON, maps a site, crawls into versioned datasets, queries and diffs those datasets, answers
questions with citations, and downloads a page's files. This plugin gives Claude Code and OpenAI Codex the
skills to use Scrawl well and connects them to Scrawl's MCP endpoint with your API key. It contains no
scraping logic of its own; Scrawl does the fetching, under its own policies and limits.

## What you need

- Access to Scrawl: the endpoint and the API key ApexAi provides for your account. Scrawl's public hosted
  access is not open yet.
- For the MCP tools: a Scrawl MCP endpoint the host can reach. Scrawl 0.8.0 accepts MCP connections only over
  loopback, so the default MCP URL is `http://127.0.0.1:8000/mcp`; there is no hosted Scrawl MCP endpoint.
- Optionally, the `scrawl` command-line tool from the Scrawl Python SDK, which the skills use for downloads,
  the setup check, AI provider profiles, and whenever the MCP server is not connected.

## Settings in Claude Code

Claude Code asks for these when you enable the plugin (`/plugin configure scrawl@apexai-scrawl` changes them):

| Setting | Default | Meaning |
| --- | --- | --- |
| `api_key` (required) | none | Your Scrawl API key, masked and kept in Claude Code's secure storage, not in `settings.json` |
| `mcp_url` | `http://127.0.0.1:8000/mcp` | Scrawl's MCP endpoint for your account |
| `base_url` | `http://127.0.0.1:8088` | Scrawl's API base URL for your account, shown to the skills for the `scrawl` CLI |

Codex has no plugin settings dialog; the Codex guide in the repository explains its configuration.

## Skills

`scrawl` (overview: which operation, cost, limits, safe handling of page content), `setup`, `scrape`, `map`,
`crawl`, `extract`, `ask`, `datasets` and `downloads`. In Claude Code and Codex they appear as `scrawl:scrape`,
`scrawl:map` and so on.

## Endpoints and privacy

The plugin connects only to the MCP URL you configure, sending your API key as an `Authorization: Bearer`
header on each request. When a skill runs the `scrawl` CLI, the CLI connects only to `SCRAWL_BASE_URL`. The
plugin has no hooks, runs no programs of its own, collects no telemetry and sends nothing anywhere else.
Pages, results and your prompts pass through your AI host (Claude or Codex) as any tool output does, and
Scrawl, operated by ApexAi, does the scraping. Scraped content is treated as untrusted data, never as
instructions.

Documentation, source and support: <https://github.com/ApexAiOfficial/scrawl-plugin>. Questions and bug
reports: GitHub issues or support@apexaiofficial.com. Licensed under the Apache License 2.0.

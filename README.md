# Scrawl plugin for Claude Code and OpenAI Codex

Scrawl's own integration for AI coding agents. It teaches Claude Code and OpenAI Codex when and how to use
Scrawl (scrape a page to Markdown or schema-checked JSON, map a site, crawl into versioned datasets, query and
diff them, ask cited questions, download a page's files) and connects them to your Scrawl server: through its
MCP endpoint, authenticated per request with your API key, or through the `scrawl` command-line tool. The
plugin holds no scraping logic; your Scrawl server does all fetching under its own policies, permissions and
limits.

One repository serves both ecosystems through their own supported mechanisms:

| | Claude Code | OpenAI Codex |
| --- | --- | --- |
| Marketplace | `.claude-plugin/marketplace.json` (`apexai-scrawl`) | `.agents/plugins/marketplace.json` (`apexai-scrawl`) |
| Plugin manifest | `plugins/scrawl/.claude-plugin/plugin.json` | `plugins/scrawl/.codex-plugin/plugin.json` |
| MCP connection | `plugins/scrawl/.mcp.json`: URL and `Authorization: Bearer` header from the plugin's settings | `plugins/scrawl/.codex-mcp.json`: bearer token from `SCRAWL_API_KEY` |
| Skills | `plugins/scrawl/skills/` (shared) | `plugins/scrawl/skills/` (shared) |

ChatGPT is **not supported yet**: it needs an OAuth 2.1 sign-in and a public HTTPS endpoint that Scrawl does
not offer today. [docs/chatgpt.md](docs/chatgpt.md) lists exactly what remains.

## Before you start

- A Scrawl server and an API key from its operator. Keys carry scopes: `scrape:write`, `jobs:read`,
  `artifacts:read` and `credits:read` by default, plus `ai:use` for JSON extraction and ask.
- For the MCP tools, the server's MCP URL. Scrawl 0.8.0 serves MCP over HTTP only on the server's own machine
  (`http://127.0.0.1:8000/mcp` by default), so the MCP route works where the agent runs on that machine. A
  hosted Scrawl MCP endpoint is not available yet. The key goes to whatever listens at that URL, so set it
  explicitly if another program on your machine may use port 8000.
- For downloads, the setup check, AI provider profiles, or a server on another machine: the `scrawl` CLI from
  the [Scrawl Python SDK](https://github.com/ApexAiOfficial/scrawl-sdk), with `SCRAWL_BASE_URL` and
  `SCRAWL_API_KEY` exported in your shell.

## Install in Claude Code

```bash
claude plugin marketplace add ApexAiOfficial/scrawl-plugin
claude plugin install scrawl@apexai-scrawl
```

To pin this release, add the tag: `claude plugin marketplace add ApexAiOfficial/scrawl-plugin#v0.1.0`.
Inside a session the same steps are `/plugin marketplace add ApexAiOfficial/scrawl-plugin` and
`/plugin install scrawl@apexai-scrawl`. Then run `/plugin configure scrawl@apexai-scrawl` to set:

| Setting | Default | Meaning |
| --- | --- | --- |
| `api_key` (required) | none | Your Scrawl API key. Masked, and kept in Claude Code's secure storage (on Linux, a `.credentials.json` file only you can read), never in `settings.json` |
| `mcp_url` | `http://127.0.0.1:8000/mcp` | Your Scrawl server's MCP endpoint. Use `https://` for any other host |
| `base_url` | `http://127.0.0.1:8088` | Your Scrawl server's API, shown to the skills for the `scrawl` CLI |

The MCP server starts only once the key is set; if you use only the `scrawl` CLI, leave the key unset and
nothing connects. Claude Code does not warn about a plain `http://` URL to another host, so check yours. More
in [docs/claude-code.md](docs/claude-code.md).

## Install in Codex

```bash
codex plugin marketplace add ApexAiOfficial/scrawl-plugin
codex plugin add scrawl@apexai-scrawl
```

To pin this release: `codex plugin marketplace add ApexAiOfficial/scrawl-plugin --ref v0.1.0`.

Codex sends the key from the `SCRAWL_API_KEY` environment variable, so export it before starting Codex. The
plugin points at `http://127.0.0.1:8000/mcp`; to use another server, override the entry under the same name:

```bash
codex mcp add scrawl --url https://scrawl.example/mcp --bearer-token-env-var SCRAWL_API_KEY
```

While `SCRAWL_API_KEY` is set, Codex sends it to that URL every time it starts. If you run no Scrawl MCP
server on this machine (for example, you use only the CLI against a remote server), switch the entry off as
shown in [docs/codex.md](docs/codex.md), so the key does not go to whatever answers on port 8000.

## Skills

| Skill | Use it to |
| --- | --- |
| `scrawl` | Choose the operation; cost, limits and quotas; handle scraped content safely; error codes |
| `setup` | Check the connection (`scrawl doctor`, the status tool), fix keys and URLs, set up your AI provider |
| `scrape` | One page or a batch of up to 20 as Markdown, links or HTML; JavaScript pages |
| `map` | List a site's pages and choose what to scrape |
| `crawl` | Run a crawl target into a new dataset version and follow the job |
| `extract` | JSON from pages, jobs or datasets with a schema, on your own AI provider |
| `ask` | Answers with citations from your datasets; search and fetch records |
| `datasets` | Fields, typed queries, version diffs, roll back, quarantine |
| `downloads` | Quote and extract a page's assets; list, read and download a job's artifacts |

Claude Code and Codex show them as `scrawl:scrape`, `scrawl:map` and so on. Each skill says whether it uses
the MCP tools or the CLI, and prefers the MCP tools when they are connected.

## Endpoints contacted

- **Your Scrawl MCP URL** (the `mcp_url` setting, or the Codex entry): every MCP request (`POST`, plus the
  optional `GET` listen stream a host may open), with `Authorization: Bearer <your key>`.
- **Your Scrawl API base URL** (`SCRAWL_BASE_URL`): only when a skill runs the `scrawl` CLI.
- **GitHub**: only when you add, install or update the plugin from this repository.

Nothing else. The plugin has no hooks, no executables, no telemetry and no network code of its own. Scrawl,
not the plugin, fetches web pages, through your server's egress and policy controls.

## Privacy

- Your API key is stored by your agent host (Claude Code's secure storage, or your environment for Codex)
  and sent only to the MCP URL you set. The plugin stores nothing.
- Prompts, tool results and scraped content pass through your AI host as any tool output does; the host's
  own terms apply. Your Scrawl server's operator processes the pages you scrape.
- The skills treat all scraped content as untrusted data, never as instructions, and never print or ask for
  your key in the conversation.

## Documentation

- [Claude Code](docs/claude-code.md), [Codex](docs/codex.md), [ChatGPT status and path](docs/chatgpt.md),
  [Self-hosted servers](docs/self-hosted.md), [Testing and validation](docs/testing.md)
- [CHANGELOG.md](CHANGELOG.md), [SECURITY.md](SECURITY.md)

## Support

Open an issue at <https://github.com/ApexAiOfficial/scrawl-plugin/issues> or write to
support@apexaiofficial.com. Report security problems privately as described in [SECURITY.md](SECURITY.md).

## License

Apache License 2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE).

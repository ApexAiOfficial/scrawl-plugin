# Scrawl plugin for Claude Code and OpenAI Codex

Skills and an MCP connection that let Claude Code and OpenAI Codex use Scrawl, the web-data service ApexAi
operates, to scrape pages, map sites, crawl into versioned datasets, extract JSON to a schema, query and diff
datasets, and answer questions with citations.

[![Validate](https://github.com/ApexAiOfficial/scrawl-plugin/actions/workflows/validate.yml/badge.svg)](https://github.com/ApexAiOfficial/scrawl-plugin/actions/workflows/validate.yml)

## Status

| | Today |
| --- | --- |
| Source | Public, under the Apache License 2.0 |
| Release | `v0.1.0`, a Git tag and a GitHub release. Pre-1.0: see [Versioning and compatibility](#versioning-and-compatibility) |
| Distribution | Installs from this GitHub repository, which is its own plugin marketplace for Claude Code and for Codex. It is not in Anthropic's or OpenAI's plugin directories, and not on npm or PyPI |
| What it needs | Access to Scrawl: the endpoint and the API key ApexAi provides for your account. Scrawl's public hosted access is not open yet (there is no public sign-up or endpoint), so the plugin is useful only to someone ApexAi has already given access |
| MCP connection | Scrawl's MCP server currently accepts only local (loopback) connections, which is why the plugin's default MCP URL is a loopback address. There is no hosted Scrawl MCP endpoint, so outside ApexAi's own environments the skills use the `scrawl` CLI |
| ChatGPT | Not supported (see [Supported hosts](#supported-hosts)) |

ApexAi's developer kits are listed at <https://apexaiofficial.com/apexsdk>, and Scrawl itself is described at
<https://apexaiofficial.com/scrawl>.

This repository is the agent plugin: it helps an AI coding agent do web-data work through Scrawl. It is not
the **Scrawl Plugin** (health, smoke tests, approvals) listed on
[apexaiofficial.com/plugins](https://apexaiofficial.com/plugins), which is a separate surface still in
development.

## Contents

- [How it works](#how-it-works)
- [Supported hosts](#supported-hosts)
- [Requirements](#requirements)
- [Quickstart](#quickstart)
- [Install](#install)
- [Configure](#configure)
- [Check the connection](#check-the-connection)
- [Skills](#skills)
- [Example prompts](#example-prompts)
- [MCP tools and the CLI](#mcp-tools-and-the-cli)
- [Troubleshooting](#troubleshooting)
- [Endpoints contacted](#endpoints-contacted)
- [Privacy](#privacy)
- [Security](#security)
- [Versioning and compatibility](#versioning-and-compatibility)
- [Update and remove](#update-and-remove)
- [Repository layout and validation](#repository-layout-and-validation)
- [Documentation](#documentation)
- [Support](#support)
- [License](#license)

## How it works

The plugin is configuration and instructions; it contains no scraping logic. Scrawl does every fetch, under
its own policies, permissions and limits.

| Part | What it does |
| --- | --- |
| Nine skills (Markdown) | Tell the agent which Scrawl operation fits a request, how to call it, what it costs, how to handle errors, and to treat everything scraped as untrusted data |
| An MCP server entry | Connects the host to Scrawl's MCP endpoint over Streamable HTTP, sending your API key as `Authorization: Bearer` on every request |
| The `scrawl` CLI (optional, installed separately) | The command-line tool from the [Scrawl Python SDK](https://github.com/ApexAiOfficial/scrawl-sdk). The skills use it for work only it can do, and whenever the MCP tools are not connected |

The plugin ships no hooks, no executables, no scripts and no telemetry. Its folder holds Markdown, JSON, an SVG
icon, and the license files.

## Supported hosts

| Host | What loads | Tested |
| --- | --- | --- |
| Claude Code (terminal) | Skills and the MCP server | Install, skill loading, and key delivery to a stand-in MCP endpoint, with Claude Code 2.1.282 |
| OpenAI Codex CLI | Skills and the MCP server | Install, skill loading, and key delivery to a stand-in MCP endpoint, with Codex CLI 0.157.1 |
| Codex IDE extension and Codex app | Expected to load the same plugin, since they share Codex's configuration | Not tested |
| claude.ai chat, Claude desktop chat, Cowork | Skills only, according to Anthropic's platform documentation | Not tested |
| ChatGPT | Not supported: ChatGPT needs a public HTTPS MCP endpoint and cannot send an API key (it signs in with OAuth 2.1), while Scrawl's MCP server is local only and takes API keys. [docs/chatgpt.md](docs/chatgpt.md) lists what would have to change | Not applicable |

## Requirements

| Requirement | Needed for | Notes |
| --- | --- | --- |
| Claude Code or the Codex CLI | Everything | Verified with Claude Code 2.1.282 and Codex CLI 0.157.1, the versions CI pins. No manifest declares a minimum version |
| Read access to github.com | Installing and updating | The host clones this repository |
| Access to Scrawl: the endpoint and the API key ApexAi provides for your account | Everything | Public hosted access is not open yet. See [API key scopes](#api-key-scopes) |
| A Scrawl MCP endpoint the host can reach | The MCP tools | Scrawl's MCP server currently accepts only loopback connections, and there is no hosted MCP endpoint. Without one, use the CLI route |
| The `scrawl` CLI: Python 3.10 or later, and the Scrawl Python SDK installed from GitHub | Downloading files to disk, `scrawl doctor`, managing AI provider profiles, and whenever the MCP tools cannot reach Scrawl | Optional. See [Install the scrawl CLI](#install-the-scrawl-cli-optional) |
| Your own AI provider profile, the `ai:use` scope, and AI features switched on by ApexAi | JSON scrapes, extract, dataset extraction and ask | These run on your AI provider account and spend your tokens. Creating or changing the profile needs the `ai:configure` scope. Markdown, links and HTML scrapes call no AI model |

### API key scopes

A key holds scopes that decide which MCP tools it sees and which calls it may make. The table follows the scope
contract published with the SDK
([`contracts/apexapi_scopes.json`](https://github.com/ApexAiOfficial/scrawl-sdk/blob/py-v0.1.0/contracts/apexapi_scopes.json)).

| Scope | Default key | Needed for |
| --- | --- | --- |
| `scrape:write` | Yes | Starting scrapes, maps, batches, crawls and asset jobs (quotes included); activating a dataset version; quarantining a record; cancelling a job |
| `jobs:read` | Yes | Listing jobs and following a job's status and result |
| `artifacts:read` | Yes | Results, artifacts, asset results and files, datasets, records, search and fetch |
| `credits:read` | Yes | The credit balance |
| `ai:use` | No | JSON scrapes, extract, dataset extraction and ask, and cancelling an AI extraction job |
| `ai:configure` | No | Managing your AI provider profiles with `scrawl ai providers` |

## Quickstart

You need access to Scrawl: the endpoint and the API key ApexAi provides for your account (public hosted access
is not open yet). The plugin's default MCP URL is the loopback address `http://127.0.0.1:8000/mcp`; see
[docs/connecting.md](docs/connecting.md) for why, and for the CLI route.

**Claude Code**

1. Install from the release tag:

   ```bash
   claude plugin marketplace add ApexAiOfficial/scrawl-plugin#v0.1.0
   claude plugin install scrawl@apexai-scrawl
   ```

2. In a Claude Code session, run `/plugin configure scrawl@apexai-scrawl`, enter the key in the masked field
   and the URLs ApexAi gave you, then run `/reload-plugins` (or restart Claude Code).
3. Check the connection from a terminal: `claude mcp get plugin:scrawl:scrawl` should show the status
   `Connected`.
4. Ask: "Check my Scrawl setup", then "Scrape https://shop.example to Markdown with Scrawl".

**Codex**

1. Install from the release tag:

   ```bash
   codex plugin marketplace add ApexAiOfficial/scrawl-plugin --ref v0.1.0
   codex plugin add scrawl@apexai-scrawl
   ```

2. Put the key in the environment Codex starts from, then start Codex:

   ```bash
   read -rs SCRAWL_API_KEY && export SCRAWL_API_KEY   # paste the key; it is not echoed or saved in history
   codex
   ```

3. Check the configuration: `codex mcp list` should show `scrawl` with `Bearer token` auth. This reads your
   configuration only; it does not contact Scrawl.
4. Ask: "Check my Scrawl setup" (this is the connection check), then "Map the pages of https://shop.example
   with Scrawl".

## Install

### Claude Code

```bash
claude plugin marketplace add ApexAiOfficial/scrawl-plugin#v0.1.0   # pinned to the release (recommended)
claude plugin install scrawl@apexai-scrawl
```

| Variant | Command |
| --- | --- |
| Follow `main` instead of a release | `claude plugin marketplace add ApexAiOfficial/scrawl-plugin` |
| Inside a session | `/plugin marketplace add ApexAiOfficial/scrawl-plugin`, then `/plugin install scrawl@apexai-scrawl` |
| For a team | Add `--scope project` to both commands. The marketplace and the plugin are recorded in the project's `.claude/settings.json`; each person still sets their own key |
| Cloning over SSH fails | Set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` before adding the marketplace |

### Codex

```bash
codex plugin marketplace add ApexAiOfficial/scrawl-plugin --ref v0.1.0   # pinned to the release (recommended)
codex plugin add scrawl@apexai-scrawl
```

To follow `main` instead, leave out `--ref v0.1.0`: `codex plugin marketplace add ApexAiOfficial/scrawl-plugin`.
Codex reads `.agents/plugins/marketplace.json` and `plugins/scrawl/.codex-plugin/plugin.json`, and ignores the
Claude Code files.

### Install the scrawl CLI (optional)

The `scrawl` command comes with the Scrawl Python SDK, which is installed from its GitHub repository. It is not
on PyPI, and the PyPI project named `scrawl` is an unrelated application.

```bash
pipx install "git+https://github.com/ApexAiOfficial/scrawl-sdk@py-v0.1.0#subdirectory=python"
scrawl --version   # scrawl 0.1.0
```

Without pipx, `pip install` the same address inside a virtual environment. Installing contacts GitHub, and
PyPI for the SDK's build and runtime dependencies.

## Configure

### Claude Code settings

Claude Code asks for these when you configure the plugin (`/plugin configure scrawl@apexai-scrawl`):

| Setting | Default | Stored in | Meaning |
| --- | --- | --- | --- |
| `api_key` (required, sensitive) | none | Claude Code's secure storage, never `settings.json`. On Linux this is a `.credentials.json` file in Claude Code's configuration directory, readable only by your user | Your Scrawl API key, sent only to `mcp_url` |
| `mcp_url` | `http://127.0.0.1:8000/mcp` | `pluginConfigs` in `settings.json` | Scrawl's MCP endpoint for your account. The default is a loopback address, because Scrawl's MCP server currently accepts only local connections |
| `base_url` | `http://127.0.0.1:8088` | `pluginConfigs` in `settings.json` | Scrawl's ApexAPI base URL for your account. The skills use it to tell you which `SCRAWL_BASE_URL` to export for the CLI |

- The MCP server is registered only once `api_key` is set. If you use only the CLI, leave the key unset and the
  plugin connects nowhere.
- Non-secret settings can also be set from a terminal, for example
  `claude plugin install scrawl@apexai-scrawl --config mcp_url=https://scrawl.example/mcp`. Enter the key in the
  masked dialog instead of `--config`, which would leave it in your shell history.
- Whatever listens at `mcp_url` receives the key, so set it only to the MCP endpoint ApexAi provides for your
  account. For any host other than this machine, use `https://`.

### Codex settings

Codex has no settings dialog for plugins. Its MCP entry is fixed at `http://127.0.0.1:8000/mcp` and sends the
key from the `SCRAWL_API_KEY` environment variable that Codex started with.

- **Another endpoint.** Codex does not expand settings in a plugin's MCP URL, so replace the entry with one of
  your own under the same name. Keep `--bearer-token-env-var`, or no key is sent:

  ```bash
  codex mcp add scrawl --url https://scrawl.example/mcp --bearer-token-env-var SCRAWL_API_KEY
  ```

  `codex mcp remove scrawl` returns to the plugin's entry. Both commands rewrite the whole `config.toml`, so copy
  it first or edit the `[mcp_servers.scrawl]` table by hand
  ([docs/codex.md](docs/codex.md#point-it-at-another-endpoint)).
- **No reachable Scrawl MCP endpoint.** While `SCRAWL_API_KEY` is set, Codex sends it to the MCP URL every
  time it starts. If you export the key only for the CLI, switch the entry off in `config.toml` in your Codex
  home:

  ```toml
  [mcp_servers.scrawl]
  url = "http://127.0.0.1:8000/mcp"
  enabled = false
  ```

  `codex mcp list` then shows the server as `disabled`, and the skills keep working through the CLI.
- **Scripted runs.** `codex exec` cannot ask you to approve a tool call; see
  [docs/codex.md](docs/codex.md#scripted-runs-codex-exec) for approving the Scrawl tools for a single run.

### CLI settings

The `scrawl` CLI takes its configuration only from environment variables, never from flags or a file. When an
agent runs it, those are the variables the agent session started with:

| Variable | Default | Meaning |
| --- | --- | --- |
| `SCRAWL_API_KEY` | none | Your API key. The CLI never takes a key from a command-line argument |
| `SCRAWL_BASE_URL` | `http://127.0.0.1:8088` | Scrawl's ApexAPI base URL for your account (the default is a loopback address). Plain `http://` is accepted only for this machine; any other host needs `https://` |
| `SCRAWL_ALLOW_INSECURE_HTTP` | unset | `1` allows plain `http://` to another host, for a trusted private network only |
| `SCRAWL_AI_API_KEY` | unset | Your AI provider key, read by `scrawl ai providers set` (which also takes it on stdin with `--key-stdin`), so it never goes on a command line |

```bash
export SCRAWL_BASE_URL=https://scrawl.example   # the ApexAPI base URL ApexAi provides for your account
read -rs SCRAWL_API_KEY && export SCRAWL_API_KEY
scrawl doctor
```

Export these before starting Claude Code or Codex; the skills never set or print them.

## Check the connection

| Route | Command | Expect |
| --- | --- | --- |
| Claude Code, plugin | `claude plugin details scrawl@apexai-scrawl` | `Skills (9)` and `MCP servers (1)` |
| Claude Code, MCP | `claude mcp get plugin:scrawl:scrawl` | The URL, `Authorization: [REDACTED]`, and the status `Connected` |
| Codex, MCP | `codex mcp list` | `scrawl`, your URL, `SCRAWL_API_KEY`, `enabled`, `Bearer token`. This shows the configuration only and does not contact the server |
| CLI | `scrawl doctor` | Checks the base URL, TLS, reachability and the key without printing the key; exit 0 when ready, 3 for a configuration problem, 5 when the endpoint cannot be reached. `scrawl --json doctor` returns the same checks as JSON |

In a Claude Code session, `/mcp` lists the server and its tools, and `/scrawl:setup` walks through the rest. In
either host, ask "check my Scrawl setup": the setup skill calls the status tool and asks you to confirm that the
account it reports is the one you expect.

## Skills

Both hosts load the same nine skills from [`plugins/scrawl/skills/`](plugins/scrawl/skills) and show them as
`scrawl:<name>`; in Claude Code you can also run them as `/scrawl:<name>`. The agent also picks a skill by
itself when a request matches its description. Each task skill prefers the MCP tools when they are connected
and says when it needs the CLI.

| Skill | Use it to |
| --- | --- |
| [`scrawl`](plugins/scrawl/skills/scrawl/SKILL.md) | Choose the operation; understand cost, limits and quotas; handle scraped content safely; read error codes ([error reference](plugins/scrawl/skills/scrawl/references/errors.md)) |
| [`setup`](plugins/scrawl/skills/setup/SKILL.md) | Check the connection (the status tool, `scrawl doctor`), fix keys and URLs, set up your AI provider profile |
| [`scrape`](plugins/scrawl/skills/scrape/SKILL.md) | Turn one page, or a batch of up to 20, into Markdown, links or HTML, and follow a scrape that is still running |
| [`map`](plugins/scrawl/skills/map/SKILL.md) | List a site's pages (start-page links and its `sitemap.xml`) and choose what to scrape |
| [`crawl`](plugins/scrawl/skills/crawl/SKILL.md) | Run a crawl target your key may use into a new dataset version, follow the job, list or cancel jobs |
| [`extract`](plugins/scrawl/skills/extract/SKILL.md) | Get JSON from pages, finished jobs or datasets, validated against a JSON Schema, on your own AI provider |
| [`ask`](plugins/scrawl/skills/ask/SKILL.md) | Answer questions from your datasets with citations; search and fetch records |
| [`datasets`](plugins/scrawl/skills/datasets/SKILL.md) | Read fields, run typed queries, diff versions, and (with your agreement) roll back a version or quarantine a record |
| [`downloads`](plugins/scrawl/skills/downloads/SKILL.md) | List, read and download a job's files. Quote and extract the files a page links to, where asset extraction is enabled for your account |

Two notes on what Scrawl offers today:

- **Browser rendering.** The `scrape` and `map` skills include instructions for a browser-rendering engine,
  used only where it is enabled. Scrawl does not offer browser rendering today. The skills treat a
  `browser_unavailable` error as "not available here" and use a plain scrape instead.
- **Page files (assets).** Extracting the images, documents or data files a page links to works only where asset
  extraction is enabled for your account. The skill quotes the job and asks for your agreement before it starts
  one, because Scrawl holds credits for it on a metered account.

## Example prompts

These need a working connection to Scrawl. `shop.example` stands for a site you want to read.

| Prompt | Skill |
| --- | --- |
| "Check my Scrawl setup" | `setup` |
| "Scrape https://shop.example to Markdown with Scrawl" | `scrape` |
| "Map the pages of https://shop.example with Scrawl" | `map` |
| "Which crawl targets can I run? Crawl one with at most 500 items" | `crawl` |
| "Get the product name and price from https://shop.example/item as JSON with Scrawl" | `extract` |
| "Answer from my Scrawl data with citations: which lamps cost under 20 EUR?" | `ask` |
| "List my Scrawl datasets and what changed in the latest version" | `datasets` |
| "List the files of my last Scrawl job and download them" | `downloads` |

## MCP tools and the CLI

The skills reach Scrawl by two routes and use one per step:

| | MCP tools | `scrawl` CLI |
| --- | --- | --- |
| Credentials | The key the host sends for the plugin | `SCRAWL_API_KEY` and `SCRAWL_BASE_URL` in your shell |
| Where it works | Where the host can reach a Scrawl MCP endpoint (Scrawl's MCP server currently accepts only loopback connections) | Any machine that can reach Scrawl's ApexAPI endpoint |
| Only here | Listing crawl targets; reading an artifact's text without saving it; MCP resources for the dataset catalog | Writing downloaded files to disk, checked against the size and SHA-256 the server records; `scrawl doctor`; managing AI provider profiles |

In Claude Code the MCP tools appear as `mcp__plugin_scrawl_scrawl__<tool>`, for example
`mcp__plugin_scrawl_scrawl__apex_scrapy_scrape_url`. The skills name only tools and arguments that exist in
the MCP tool contract vendored in [`contracts/mcp_tools.json`](contracts/mcp_tools.json), and CI checks this.

### Limits per call

From the vendored MCP tool contract:

| Operation | Limit |
| --- | --- |
| Batch scrape | 1 to 20 URLs |
| Map | 1 to 500 URLs (default 100) |
| Server-side wait for a scrape or map | Up to 60 seconds (default 30) |
| Crawl | Up to 10,000 items and 1,800 seconds; these are also the defaults, so the skills pass smaller caps |
| Artifact text per read | Up to 50,000 characters (default 12,000) |
| Dataset version query | Up to 20 filters; up to 200 rows per page (default 50) |
| Dataset extraction | 1 to 200 records (default 50) |
| Asset job | Up to 1,000 files (default 100) and 150 MiB (default 50 MiB) |
| Ask | A question of up to 2,000 characters |

Agent hosts cut off long shell commands, so the skills keep every CLI `--wait` at 60 seconds or less, then
follow the job by its ID.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| No Scrawl MCP tools in Claude Code | `api_key` is not set, so the server is not registered | `/plugin configure scrawl@apexai-scrawl`, then `/reload-plugins` |
| Connection refused at the MCP URL | Nothing listens there | Correct the URL to the MCP endpoint ApexAi provides. Without a reachable endpoint, leave `api_key` unset and use the CLI |
| 401 `unauthorized` (no key reached the server) or `invalid_token` | The key is missing or not accepted | Set a valid key. Scrawl has no browser sign-in |
| Some Scrawl tools are missing | The key lacks their scope, or the MCP endpoint is limited to read-only tools | Ask ApexAi (support@apexaiofficial.com) for a key with the scope ([API key scopes](#api-key-scopes)), or use the CLI for that step |
| `forbidden` (CLI exit 3) | The key lacks the scope for this call | Ask ApexAi for the scope. `scrawl ai providers` needs `ai:configure` |
| `scrawl: command not found` | The CLI is not installed | [Install the scrawl CLI](#install-the-scrawl-cli-optional) |
| `scrawl doctor` fails the `base_url` check with `Refusing to send the API key over plain HTTP` (exit 3) | `SCRAWL_BASE_URL` is `http://` to another host | Use Scrawl's `https://` URL |
| `scrawl doctor` fails the `reachable` check with `Connection failed` (exit 5) | Nothing answers at `SCRAWL_BASE_URL` | Check it against the endpoint ApexAi provided |
| `unavailable` (CLI exit 5) on extract or ask | AI features are switched off | Only ApexAi can switch them on: ask support@apexaiofficial.com |
| `ai_auth`, `ai_quota`, `ai_rate_limited` (CLI exit 5) | Your AI provider refused the key, is out of quota, or rate-limited the call | Fix the profile, then `scrawl ai providers test main` (for a profile named `main`) |
| `browser_unavailable` (CLI exit 5) | Browser rendering is not enabled | Scrawl does not offer browser rendering today; use a plain scrape |
| `rate_limited` or `too_many_active_jobs` (CLI exit 5) | A per-minute allowance or the account's job cap is reached | Wait, or cancel a job. For reads and for commands that start a job, the CLI has already retried twice, honouring `Retry-After` |
| Codex sends no key after `codex mcp add` | The override has no `--bearer-token-env-var` | Add it again with `--bearer-token-env-var SCRAWL_API_KEY` |

A job that ran and failed is a result, not an error: its `status` is failed and its `error_code` says why. CLI
exit codes are 0 success, 1 the job or an item failed, 2 usage, 3 authentication or configuration, 4 still
running at the deadline, 5 any other API or connection error. The full table of codes is in the
[error reference](plugins/scrawl/skills/scrawl/references/errors.md).

## Endpoints contacted

| Destination | When | What is sent |
| --- | --- | --- |
| Your Scrawl MCP URL (Claude Code's `mcp_url`, or the Codex entry) | Claude Code: only once `api_key` is set. Codex: at every start while `SCRAWL_API_KEY` is set and the entry is enabled | Every MCP request (`POST`, and the optional `GET` stream a host may open), each with `Authorization: Bearer <your key>` |
| Your Scrawl ApexAPI base URL (`SCRAWL_BASE_URL`) | Only when a skill runs the `scrawl` CLI | CLI requests with your key |
| github.com | When you add, install or update the plugin, or install the CLI | Git and package downloads; no key |
| PyPI (pypi.org and files.pythonhosted.org) | When you install the CLI | Downloads of the SDK's build and runtime dependencies; no key |

Nothing else. The plugin has no network code of its own. Scrawl, not the plugin, fetches web pages, through
its own egress and policy controls.

## Privacy

- **Your key.** Claude Code keeps it in its secure storage; Codex and the CLI read it from your environment.
  The plugin itself stores nothing.
- **What your AI host sees.** Prompts, tool results and scraped content pass through Claude Code or Codex like
  any other tool output, and the host's own terms apply.
- **What Scrawl sees.** ApexAi operates Scrawl, which processes the pages you ask it to fetch and the requests
  your key makes.
- **In the conversation.** The skills never ask you to type a key into the chat, never put one on a command
  line, and never print one.
- **Scraped content is untrusted.** Every skill tells the agent to treat page text, extracted values, dataset
  records, answers, citations and file names as data, never as instructions; never to let them choose a URL,
  command, file, setting or destination; and never to open a downloaded file with a program that could run
  it.

## Security

Report a vulnerability privately by email to **support@apexaiofficial.com**. Do not open a public issue for
it. Include what you found, how to reproduce it, the plugin version, and the host and its version.
[SECURITY.md](SECURITY.md) lists what the plugin promises.

Practices worth keeping:

- Give each key only the scopes it needs, especially for unattended runs.
- Use `https://` for any endpoint that is not on this machine. Neither host refuses a plain `http://` URL to
  another host.
- Make sure the program listening at the MCP URL is Scrawl: whatever answers there receives the key.
- Treat downloaded files as untrusted; keep them in a new folder outside version control.

Report a vulnerability in the Scrawl service itself the same way. The CLI and SDKs are covered by
[scrawl-sdk](https://github.com/ApexAiOfficial/scrawl-sdk).

## Versioning and compatibility

| Item | Value |
| --- | --- |
| Plugin version | `0.1.0`, the same in both host manifests |
| Versioning | [Semantic Versioning](https://semver.org/). Before 1.0, any release may change behaviour: pin a tag. Changes are recorded in [CHANGELOG.md](CHANGELOG.md) |
| Hosts | Verified with Claude Code 2.1.282 and Codex CLI 0.157.1. Other versions may work but are not tested |
| `scrawl` CLI | The skills and CI use the Scrawl Python SDK at `py-v0.1.0` |
| MCP tool contract | [`contracts/mcp_tools.json`](contracts/mcp_tools.json), identical to the contract published with scrawl-sdk `py-v0.1.0`. A later Scrawl version may add, change or remove tools |

## Update and remove

**Claude Code**

```bash
claude plugin marketplace update apexai-scrawl
claude plugin update scrawl@apexai-scrawl          # restart Claude Code to apply
claude plugin uninstall scrawl@apexai-scrawl
claude plugin marketplace remove apexai-scrawl
```

**Codex**

```bash
codex plugin marketplace upgrade apexai-scrawl
codex plugin remove scrawl@apexai-scrawl
codex plugin marketplace remove apexai-scrawl
```

A marketplace pinned to `v0.1.0` stays on that release when you update it. To move to a newer release, run the
remove commands above, add the marketplace again with the newer tag, and install the plugin again. In Claude
Code, uninstalling the plugin (or removing its marketplace, which also uninstalls it) deletes the stored key
and the plugin's settings, so configure it again afterwards. Codex stores no key (it stays in your
environment), but an `[mcp_servers.scrawl]` table you added yourself stays in `config.toml`, and keeps
receiving the key, until you remove it.

## Repository layout and validation

| Path | Contents |
| --- | --- |
| [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) | Claude Code marketplace `apexai-scrawl` |
| [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) | Codex marketplace `apexai-scrawl` |
| [`plugins/scrawl/.claude-plugin/plugin.json`](plugins/scrawl/.claude-plugin/plugin.json) | Claude Code manifest and settings |
| [`plugins/scrawl/.codex-plugin/plugin.json`](plugins/scrawl/.codex-plugin/plugin.json) | Codex manifest |
| [`plugins/scrawl/.mcp.json`](plugins/scrawl/.mcp.json) | Claude Code MCP entry: URL and bearer header from the settings |
| [`plugins/scrawl/.codex-mcp.json`](plugins/scrawl/.codex-mcp.json) | Codex MCP entry: bearer token from `SCRAWL_API_KEY` |
| [`plugins/scrawl/skills/`](plugins/scrawl/skills) | The nine skills, shared by both hosts |
| [`contracts/`](contracts) | The vendored MCP tool contract and its manifest |
| [`tests/`](tests), [`tools/`](tools) | Validation and a stand-in MCP endpoint; not part of the plugin |

Run the static checks in a virtual environment (CI uses Python 3.12):

```bash
python -m pip install pytest "git+https://github.com/ApexAiOfficial/scrawl-sdk@py-v0.1.0#subdirectory=python"
SCRAWL_PLUGIN_REQUIRE_CLI=1 python -m pytest tests
```

They check that both hosts' manifests agree, that keys reach each host only the supported way, that every
`scrawl` command in the skills and docs parses with the real CLI, and that every MCP tool and argument the
skills name exists in the contract. [docs/testing.md](docs/testing.md) adds install checks in isolated host
homes and key-delivery checks against the stand-in endpoint. The
[Validate](.github/workflows/validate.yml) workflow runs all of this on GitHub-hosted runners for every push
to `main` and every pull request.

## Documentation

| Guide | Covers |
| --- | --- |
| [docs/claude-code.md](docs/claude-code.md) | Claude Code install, settings, checks, other Claude surfaces |
| [docs/codex.md](docs/codex.md) | Codex install, key, custom endpoint, switching the MCP entry off, scripted runs |
| [docs/connecting.md](docs/connecting.md) | The plugin's default URLs, what Scrawl's MCP endpoint expects, and the CLI route |
| [docs/chatgpt.md](docs/chatgpt.md) | Why ChatGPT is not supported, and what would change |
| [docs/testing.md](docs/testing.md) | Static checks, install checks, key-delivery and end-to-end procedures |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |
| [SECURITY.md](SECURITY.md) | Security promises and scope |

## Support

- Bugs and questions about the plugin: [GitHub issues](https://github.com/ApexAiOfficial/scrawl-plugin/issues),
  or support@apexaiofficial.com.
- Access to Scrawl and integration questions: sales@apexaiofficial.com. Public hosted access is not open yet.
- Security problems: email support@apexaiofficial.com, never a public issue.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

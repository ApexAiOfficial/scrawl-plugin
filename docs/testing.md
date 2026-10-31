# Testing and validation

## Static checks (CI runs these on every push and pull request)

```bash
python -m pip install pytest "git+https://github.com/ApexAiOfficial/scrawl-sdk#subdirectory=python"
SCRAWL_PLUGIN_REQUIRE_CLI=1 python -m pytest tests
```

The tests check that:

- both hosts' marketplaces and manifests agree, the key reaches Claude Code only through the sensitive
  `api_key` setting and Codex only through `SCRAWL_API_KEY`, and the plugin has no hooks, executables or
  `.app.json`;
- every skill has the front matter both hosts read and says which route it uses;
- every `scrawl` command in the skills and docs parses with the real CLI parser, and every exit code the
  skills promise for an error code is the one the real CLI returns;
- every MCP tool and argument the skills name exists in `contracts/mcp_tools.json` (vendored from
  scrawl-sdk with `python tools/sync_contract.py <scrawl-sdk checkout>`), with every required argument;
- no `scrawl` command waits longer than 60 seconds or relies on a longer default wait (a host would cut it
  off before it printed the job ID), and every task skill carries the same safety rules;
- nothing private is published and examples use reserved hosts (`.example`, `.test`, loopback).

## Install checks in isolated homes

These never touch your own Claude Code or Codex configuration:

```bash
work=$(mktemp -d) && mkdir -p "$work/claude" "$work/codex"

export CLAUDE_CONFIG_DIR="$work/claude"
claude plugin validate --strict .
claude plugin validate --strict ./plugins/scrawl
claude plugin marketplace add "$PWD"
claude plugin install scrawl@apexai-scrawl
claude plugin list --json          # mcpServers.scrawl: url ${user_config.mcp_url}, Bearer ${user_config.api_key}
claude plugin details scrawl@apexai-scrawl

export CODEX_HOME="$work/codex"
codex plugin marketplace add "$PWD"
codex plugin add scrawl@apexai-scrawl
codex mcp list --json              # scrawl: http://127.0.0.1:8000/mcp, bearer_token_env_var SCRAWL_API_KEY
codex debug prompt-input "hi"      # lists the skills as scrawl:scrape, scrawl:map, ...
```

## Key delivery without a Scrawl server

`tools/mcp_probe.py` is a stand-in MCP endpoint that only records whether each request carried the expected
bearer token (never the token itself). CI uses it to prove that each host sends the configured key to the
configured URL:

```bash
python3 tools/mcp_probe.py --port 18765 --key probe-key --log "$work/claude-probe.jsonl" &
CLAUDE_CONFIG_DIR="$work/claude" claude plugin install scrawl@apexai-scrawl \
  --config mcp_url=http://127.0.0.1:18765/mcp --config api_key=probe-key
CLAUDE_CONFIG_DIR="$work/claude" claude mcp get plugin:scrawl:scrawl     # Status: Connected
python3 tools/mcp_probe.py --check "$work/claude-probe.jsonl"             # initialize and tools/list, all authenticated
kill %1

python3 tools/mcp_probe.py --port 8000 --key probe-key --log "$work/codex-probe.jsonl" &
CODEX_HOME="$work/codex" SCRAWL_API_KEY=probe-key codex debug prompt-input "hi" > /dev/null
python3 tools/mcp_probe.py --check "$work/codex-probe.jsonl"
kill %1
```

Use a throwaway value like `probe-key` here, never a real key: `--config` puts it on the command line.

## End-to-end runs against a real Scrawl server

These make real model calls and real scrapes, so they run against a test server (for example a lab
deployment on this machine) with a test key whose scopes cover the skill under test. Use isolated homes as
above; each needs its own Claude or Codex sign-in.

**Claude Code**

```bash
export CLAUDE_CONFIG_DIR="$work/claude"
claude plugin install scrawl@apexai-scrawl --config mcp_url=http://127.0.0.1:8000/mcp
claude                                            # then: /plugin configure scrawl@apexai-scrawl (masked key)
claude mcp get plugin:scrawl:scrawl               # Status: connected
claude -p "Use Scrawl to scrape https://lab.test/ and summarise it" \
  --allowedTools "mcp__plugin_scrawl_scrawl__apex_scrapy_scrape_url,mcp__plugin_scrawl_scrawl__apex_scrapy_scrape_result"
```

**Codex**

```bash
export CODEX_HOME="$work/codex" SCRAWL_API_KEY=...   # the test key
codex mcp add scrawl --url http://127.0.0.1:8000/mcp --bearer-token-env-var SCRAWL_API_KEY   # only if not the default
codex exec "Use Scrawl to map https://lab.test/ and list its sections"
```

**The CLI route** (both hosts): export `SCRAWL_BASE_URL` and `SCRAWL_API_KEY` before starting the agent, then
ask for a download, for example "download the images from https://lab.test/gallery with Scrawl".

For each run, confirm in the server's logs that the calls arrived under the test key's account, that a key
without a scope sees only the tools its scopes allow, and that the agent did not follow instructions planted
in a test page.

Suggested prompts, one per skill: setup ("check my Scrawl setup"), scrape, map, crawl (with a lab crawl
target), extract (with a schema and an AI profile), ask (with a crawled dataset), datasets (query and diff two
versions), downloads (quote, then extract assets).

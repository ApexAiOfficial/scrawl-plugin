# Scrawl errors: codes, statuses, CLI exit codes and what to do

Read this when a Scrawl MCP tool or `scrawl` command fails. The same server codes reach both routes:

- **MCP tool error:** the text starts with `[code]`, then the message, then `Fix:` and a remedy.
- **CLI:** stderr shows `error: [code] message (request req_…)`; the exit code is in the last column.
  The CLI already retries rate limits and transient gateway errors (honouring Retry-After) before it gives up.

## API codes

| Code | HTTP | CLI exit | Meaning | What to do |
| --- | --- | --- | --- | --- |
| `unauthorized` | 401 | 3 | The API key is missing, invalid or revoked | Ask the user to set a valid key (setup skill); never guess or retry |
| `forbidden` | 403 | 3 | The key lacks the scope this call needs, or Scrawl refuses this feature for the account (for example a custom AI endpoint on a hosted account) | Name the operation; the user needs a key with that scope from ApexAi |
| `account_not_active` | 403 | 3 | The key's hosted account cannot act now (for example, suspended) | Tell the user; the account owner resolves it where the account is managed (the `Fix:` text says how); nothing to retry |
| `bad_request` | 400 | 5 | Refused before any work started | Read the message; fix the request |
| `dispatch_refused` | 400 | 5 | A gate refused the job (for example, a crawl target the key may not use) | List the allowed crawl targets; do not retry the same call |
| `egress_required` | 400 | 5 | The job needs a usable proxy and the key has none; nothing was sent | Tell the user the account needs a proxy before asset extraction |
| `insufficient_credits` | 402 | 5 | The hosted account cannot cover the job's credit hold | Show the balance; narrow the job or ask the user to add credits |
| `not_found` | 404 | 5 | Unknown, or not owned by this key | List jobs or datasets to find the right ID; never guess IDs |
| `conflict` | 409 | 5 | A request with the same idempotency key is still running | Wait, then check the job list |
| `payload_too_large` | 413 | 5 | The request body is too large | Shorten the schema, instruction or URL list |
| `invalid_request` | 422 | 5 | Malformed or outside a bound | Check the arguments against the limits; fix and resend once |
| `budget_exceeded` | 422 | 5 | The estimate is above `max_credits`; nothing was reserved | Quote again; raise the cap only with the user's agreement, or narrow the job |
| `invalid_artifact_name`, `unsafe_artifact_path` | 422 | 5 | Not a file name from the job's artifact list | List the job's artifacts and use a listed name |
| `rate_limited` | 429 | 5 | Too many requests for this account | MCP: wait the Retry-After seconds, then retry once. CLI: it already retried, so wait about a minute before one more attempt |
| `too_many_active_jobs` | 429 | 5 | The account already has its maximum of running or queued jobs; or, for a browser render, the renderer is busy (the `Fix:` text says so) | Wait for a job to finish, or cancel one with the user's agreement; a busy renderer: retry in a few seconds |
| `internal_error` | 500 | 5 | Unexpected server failure | Retry once; then report it with the request ID |
| `submission_failed` | 500 | 5 | An earlier submit with this idempotency key failed | List jobs, then submit again |
| `ai_auth`, `ai_quota`, `ai_rate_limited`, `ai_refused`, `ai_timeout`, `ai_unavailable`, `ai_bad_request`, `ai_context_overflow`, `ai_malformed_output`, `ai_endpoint_forbidden`, `ai_provider_error` | 502 | 5 | The user's own AI provider failed | Report which (key, quota, limit, refusal, model, size); the user fixes the AI profile (setup skill) |
| `unavailable` | 503 | 5 | Something the operation needs is not configured or not running, for example AI features switched off (`apex_scrapy_ai_status` reports `enabled` false) | Retry later; AI features only ApexAi can turn on |
| `browser_unavailable` | 503 | 5 | Browser rendering is not available | Scrape with the static engine instead |
| `render_not_supported` | none | 5 | Raised by the CLI: `--browser` was asked for, but another engine rendered the result | Scrawl did not render it in a browser; use a plain scrape |

The MCP server may also report `internal` (an unexpected failure; retry once) and `key_revoked` (use an active
key).

## MCP connection errors (before any tool runs)

| HTTP | Body | Meaning | What to do |
| --- | --- | --- | --- |
| 401 | `unauthorized` | No `Authorization: Bearer` header reached the server | The plugin's API key is not set (setup skill) |
| 401 | `invalid_token` | The key was not accepted | The user sets a valid key; there is no browser sign-in |
| 429 | JSON-RPC error with `rate_limited` | Per-account requests-per-minute allowance used up | Wait the Retry-After seconds (about a minute if none is shown) |
| 503 | `temporarily_unavailable` | The server cannot check keys right now | Retry after a few seconds |
| none | connection refused or name not found | Nothing answers at the MCP URL | No Scrawl MCP endpoint answers at that URL: correct it, or use the CLI (setup skill) |

## Failed jobs

A job that ran and failed is returned as a result, not raised: `status` is failed and `error_code` is one of,
for example, `fetch_failed`, `job_timeout`, `egress_unavailable`, `preflight_denied`, `render_interrupted` or
`internal_error`, with a readable `error` or `failure_reason`. The CLI exits 1 for it. Report the reason; a
`preflight_denied` page is blocked by policy (robots.txt, domain policy) and must not be retried.

## CLI exit codes

| Exit | Meaning |
| --- | --- |
| 0 | Success |
| 1 | The job or a batch item failed; a download did not match its size or SHA-256 (it was not written), or the job's files are not available; `scrawl ai providers test main` failed |
| 2 | Usage error, or a file already exists where a download would go (nothing is overwritten) |
| 3 | Authentication or configuration: 401 or 403, no API key, an unusable base URL or AI key, a TLS failure in `scrawl doctor` |
| 4 | Still pending or running at the deadline: the job continues; follow it up with its ID |
| 5 | Any other API or connection error |

`scrawl job`, `scrawl jobs` and the other read commands exit 0 whatever state the job is in: read `status` in
their JSON.

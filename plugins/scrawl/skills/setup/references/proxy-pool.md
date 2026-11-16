# A pool of proxies, and the proxy health report

`scrawl proxy health` is a free advisory report on the proxy (its exit's network type and whether ordinary sites
block it); it does not decide whether jobs may run. Datacenter exits are blocked by many sites, residential ones
far less: the choice is the user's, and a blocked page is still charged (see the charging rule below).

**A pool of proxies instead (hosted accounts).** In `pool` or `required_pool` mode, jobs leave through a pool entry
that has passed its test; in `direct` mode (the default), through the single proxy above. The same rules apply to
the URL: it comes from `SCRAWL_PROXY_URL` (or `--url-env NAME`) or from the user's own terminal (`--url-stdin`).

```bash
scrawl proxy pool add --label home-1            # reads SCRAWL_PROXY_URL
scrawl proxy pool test home-1                   # an entry carries jobs only after it passes
scrawl proxy pool mode pool                     # or required_pool; direct goes back to the single proxy
scrawl proxy pool list                          # the mode and the entries (credentials masked)
```

`scrawl doctor` is ready in a pool mode only when an entry has passed its test.

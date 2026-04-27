# Chromium proxy bypass: respect user's loopback exemption

## Background

Playwright's Chromium browser type translates a user-supplied
`proxy.bypass` string (a comma-separated host list) into Chromium's
`--proxy-bypass-list=` command-line argument when launching the browser.
Chromium has a special token, `<-loopback>`, that — when present in the
bypass list — causes loopback traffic (`localhost`, `127.0.0.1`, `::1`,
etc.) to be sent through the proxy server instead of being delivered
directly. By default, Playwright **forces** `<-loopback>` into the
bypass list so that loopback hosts under test still get routed through
the user's proxy. Users can disable this default with the
`PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK` environment
variable.

The translation is performed inside Playwright's Chromium launcher when
it computes the `--proxy-bypass-list=` argument from `proxy.bypass`.

## The bug

When a user explicitly opts loopback hosts out of their proxy by
including `localhost`, `127.0.0.1`, or `::1` in `proxy.bypass`,
Playwright still appends `<-loopback>` to the resulting
`--proxy-bypass-list=` value. Because `<-loopback>` overrides individual
loopback host entries, this silently sends loopback traffic through the
proxy — the opposite of what the user asked for.

## Reproduction (input → current vs. expected `--proxy-bypass-list=` value)

| Launch options                                                   | Current (buggy)                | Expected                |
| ---------------------------------------------------------------- | ------------------------------ | ----------------------- |
| `proxy: { server: 'http://proxy:8080', bypass: 'localhost' }`    | `localhost;<-loopback>`        | `localhost`             |
| `proxy: { server: 'http://proxy:8080', bypass: '127.0.0.1' }`    | `127.0.0.1;<-loopback>`        | `127.0.0.1`             |
| `proxy: { server: 'http://proxy:8080', bypass: '::1' }`          | `::1;<-loopback>`              | `::1`                   |
| `proxy: { server: 'http://proxy:8080', bypass: 'localhost,example.com' }` | `localhost;example.com;<-loopback>` | `localhost;example.com` |

The values listed under "Expected" are the literal strings the resulting
Chrome argument must contain (entries are joined by `;`). Whitespace
around individual entries in `proxy.bypass` continues to be trimmed
before any decision is made.

## Behavior that must not regress

- When `proxy.bypass` contains **only** non-loopback hosts (e.g.
  `'example.com,foo.test'`), `<-loopback>` is still appended (so the
  resulting list is `example.com;foo.test;<-loopback>`).
- When `proxy.bypass` is unset, `--proxy-bypass-list=<-loopback>` is
  still emitted (provided the disable env var is unset).
- When `PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK` is set,
  `<-loopback>` is suppressed regardless of `proxy.bypass`.
- An explicit `<-loopback>` token already present in `proxy.bypass`
  must not be duplicated.
- The `--proxy-server={server}` argument continues to be emitted
  whenever a proxy is configured.

## Scope

The fix lives in Playwright's Chromium launch-argument computation
(`packages/playwright-core/src/server/chromium/`). The change should be
purely in the logic that decides whether to push the default
`<-loopback>` token onto the proxy bypass list — no public API
additions, no new exports, no changes elsewhere in the project.

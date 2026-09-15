# 13 — GoHighLevel MCP Server (HTTP Transport)

## What was added

`.mcp.json` (project scope, committed to this repo) now registers
GoHighLevel's own hosted MCP server:

```json
{
  "mcpServers": {
    "ghl": {
      "type": "http",
      "url": "https://services.leadconnectorhq.com/mcp/anthropic/v2"
    }
  }
}
```

Anyone opening this repository in Claude Code (CLI, desktop, or web) gets
this server offered automatically. It is a **separate integration path**
from `src/csuite/ghl/api_client.py` — see the comparison below.

## What this is / isn't

- This is GHL's own MCP endpoint, hosted by LeadConnector — not code we
  wrote or control. We only point Claude Code at the URL.
- No token, header, or credential is stored in `.mcp.json` or anywhere else
  in this repo. Connecting is an interactive, per-user action: the first
  time a person's Claude Code session tries to use the `ghl` server, it
  will prompt them through whatever auth flow GHL's endpoint requires
  (expect an OAuth/location-consent flow, consistent with how GHL gates
  the rest of its API — see `docs/12-live-ghl-connection.md`). Nobody's
  credentials are shared by adding this file; each user authorizes their
  own GHL account/location.
- Nothing in this system is switched to live/paid mode by this change.
  `GHLAdapter` still defaults to `dry_run=True`, and the MCP server here is
  additive tooling for interactive Claude Code sessions, not something the
  `csuite` orchestrator or agents call programmatically.

## MCP server vs. `GHLApiClient` — when to use which

| | `ghl` MCP server (`.mcp.json`) | `src/csuite/ghl/api_client.py` |
|---|---|---|
| Used by | A human's interactive Claude Code session (this CLI/IDE/web) | The Python `csuite` package (`GHLAdapter`, agents, orchestrator) |
| Auth | Per-user OAuth/consent flow through the MCP connection, handled by Claude Code | `GHL_ACCESS_TOKEN` env var, read once at `GHLApiClient` construction |
| Scope of actions | Whatever tools GHL's MCP server exposes (defined by GHL, not this repo) | The specific endpoints wired in `adapter.py`'s live-action table (docs/12) |
| Governed by this system's guardrails (dry-run, tenant isolation, margin alerts, onboarding state machine)? | No — it's a direct line from a person's editor session to their own GHL account | Yes — every call still goes through `GHLAdapter` |

Use the MCP server for ad hoc, human-driven exploration of a GHL
account/location from inside Claude Code (e.g. "what custom fields does
this location have?"). Use `GHLApiClient`/`GHLAdapter` for anything the
Revenue OS itself needs to do programmatically, because that path carries
the dry-run gate and every other safety control described in
`docs/09-credentials-and-ghl-ids.md` and `docs/12-live-ghl-connection.md`.

## Verifying it works

From a Claude Code session opened against this repo:

```
claude mcp list
```

should show `ghl` with type `http`. The first tool call against it will
trigger GHL's own authorization flow in the browser; complete that with an
account you're authorized to connect, then retry the call.

If a connection ever needs to be removed:

```
claude mcp remove ghl --scope project
```

# NDASentry MCP Server

> Anonymous NDA risk analysis for AI agents. $9 per report. No signup, no account, no data retention.

NDASentry exposes a multi-stage NDA risk analysis pipeline as MCP tools so any AI agent (Claude Desktop, Cursor, Cline, etc.) can review NDAs on behalf of its user — discover risky clauses, flag missing protections, return a structured risk report — without asking the user to leave the agent, create an account, or wait for a lawyer.

The wedge: every other legal MCP server in this space requires an account, an enterprise login, or attorney-in-the-loop review. NDASentry is designed to be the simplest path for a personal AI agent: call anonymously, pay $9 with a card, get a structured analysis in under a minute.

## What it does

Two tools:

- **preview_nda_risk(pdf_base64, filename)** — Free preview. Stages the NDA, runs cheap-stage detection (regex-based clause finding, no LLM calls), returns a clause-level summary plus a Stripe payment link. Safe to expose to anonymous agent traffic; zero LLM cost on the preview path.

- **get_nda_report(session_token)** — Paid full report. Polls payment status, then runs the full multi-stage LLM pipeline (qualifier, detector, scorer, critic, synthesizer, decision policy) and returns structured JSON with clause-level risk findings, aggressive-clause signals, missing protections, a critique, and a recommended action.

The full pipeline output is designed for agent consumption — flat structured JSON, every clause carries risk level, evidence, and reasoning, so agents can filter, summarize, or route based on what their user cares about.

## Quick start (hosted)

Point your MCP client at the public hosted endpoint:

    https://nda-mcp-production.up.railway.app/mcp

### Claude Desktop config

Add to claude_desktop_config.json:

    {
      "mcpServers": {
        "ndasentry": {
          "url": "https://nda-mcp-production.up.railway.app/mcp",
          "transport": "streamable-http"
        }
      }
    }

Restart Claude Desktop. The two tools will appear in the agent's tool catalog.

### Example agent prompt

> Review this NDA and tell me if there is anything I should push back on before signing.
> [attach NDA PDF]

The agent calls preview_nda_risk first, returns a preview plus a payment URL. You pay $9 in your browser. The agent calls get_nda_report and returns the full analysis.

## Self-host

For users who want their own instance, or local development:

    git clone https://github.com/valtirman/ndasentry-mcp.git
    cd ndasentry-mcp/mcp_server
    python -m venv .venv-mcp
    source .venv-mcp/bin/activate
    pip install -r requirements.txt

    export NDASENTRY_BACKEND_URL=https://ndasentry.ai
    python -m mcp_server.server

The server listens on http://localhost:1966/mcp by default. Point your MCP client at it:

    {
      "mcpServers": {
        "ndasentry": {
          "url": "http://localhost:1966/mcp",
          "transport": "streamable-http"
        }
      }
    }

### Configuration

| Env var | Default | Purpose |
|---|---|---|
| NDASENTRY_BACKEND_URL | http://localhost:8001 | Backend API that runs the analysis pipeline |
| PORT | 1966 | Port the MCP server binds to |
| MCP_ALLOWED_HOSTS | (empty) | Comma-separated production hosts to add to DNS rebinding allowlist |
| MCP_ALLOWED_ORIGINS | (empty) | Comma-separated production origins to add to DNS rebinding allowlist |

The backend (ndasentry.ai by default for the hosted version) handles document analysis and Stripe payment verification. The MCP server is a thin protocol adapter that does not reimplement any pipeline logic. The same backend serves the web product at https://ndasentry.ai.

## Tools reference

### preview_nda_risk

Input:
- pdf_base64 (string): base64-encoded PDF bytes, max 10 MB
- filename (string): the PDF filename

Output: JSON with session_token, payment_url (Stripe link with the session token bound as client_reference_id), clause_summary, missing_required_clauses, a labeled sample clause showing the shape of a paid analysis, and a disclaimer.

### get_nda_report

Input:
- session_token (string): from the preview_nda_risk response

Output: Full structured AnalysisReport JSON with clauses, risk scores, critique, completeness, qualification, aggressive-clause signals, recommended action, and disclaimer. If payment is not yet complete, returns a polling status response instead.

## Disclaimer

NDASentry is a contract risk screening tool, not a law firm. Output is not legal advice and does not create an attorney-client relationship. For binding legal interpretation or high-stakes decisions, consult licensed counsel.

## Privacy

The hosted backend at ndasentry.ai is designed around an "evaporates" model:
- Documents are processed in memory only, never written to disk
- Reports are cached in RAM for 5 minutes after generation, then deleted
- No account, no email collection, no document retention

## About

Built by Val Tirman at FrontRange Mountain AI LLC. Solo indie effort. The web product runs at https://ndasentry.ai; this MCP server is the agent-facing channel on the same backend.

If you build something with NDASentry MCP, drop a note: **frontrangesupport@gmail.com**. Genuinely interested in what agents do with this.


## License

MIT — see [LICENSE](LICENSE) file in the repository root.

# Trusted Community Marketplace

An open-source professional services marketplace reference for **AI agent governance, human approval, community security and permissioned procurement**.

[A2Z SOC](https://a2zsoc.com) develops this independent experimental project. It is not affiliated with or endorsed by CNCF, Discord or Slack. No community installation, outreach, payment or contract signature occurs.

## Run the complete synthetic engagement

Python 3.12+ with no runtime dependencies:

```sh
python -m unittest discover -s tests -v
python -m marketplace.demo
```

The demonstration creates a buyer request, lets a supplier agent draft a proposal, blocks agent commitment and an unrelated organization's read, obtains human approvals, creates an isolated engagement, submits a synthetic deliverable and records human acceptance. Payment stays disabled. See [the recorded result](evidence/demo.json).

## What works

- SQLite reference persistence for memberships, opted-in service listings, invited requests, proposals and engagement rooms.
- Explainable matching on public service tags. Supplier credentials remain explicitly supplier-asserted.
- Role and organization checks on every domain read/action, revocation, copied read results, and human-only commitments.
- Proposal terms copied into engagements, single award per request in the local execution model, acceptance criteria and rework.
- Access-controlled audit views with a hash-linked action sequence.
- Public-channel-only connector consent preflight. No network transport.

## What does not ship

This is a trusted-local-call domain prototype, not a production multi-tenant service. Caller-created Principal objects are not authenticated identities. There is no production HTTP API or dashboard, verified credentials provider, signed delegation, cryptographic human proof, payment/escrow, legally binding signature, dispute adjudication, live Slack MCP or Discord connection, model invocation or autonomous moderation.

The local DB administrator can change records and recompute audit hashes. The log does not attest payload history. SQLite use is single-process reference logic, not verified concurrent procurement. Do not expose these methods to untrusted clients.

## Platform relationship

The [Permissioned Contributor Agent](https://github.com/AAH20/permissioned-contributor-agent) supplies a separate tested reference for consent, LangGraph synthetic due diligence, quote validation and bounded evaluation loops. This repository links it rather than pretending that its synthetic findings verify marketplace suppliers. See [integration contract](docs/integration.md).

## Documentation

- [Architecture and production backlog](docs/architecture.md)
- [CNCF collaboration proposal](docs/cncf-pilot.md)
- [KPIs and improvement loop](docs/evaluation.md)
- [Connector policies](docs/connectors.md)
- [Public and private boundaries](docs/publication.md)

Apache-2.0. Contributions and support: [A2Z SOC](https://a2zsoc.com). This repository is an inspectable reference foundation for a much broader professional services marketplace.

## Interactive local demonstration

```sh
python -m marketplace.web
```

Open `http://127.0.0.1:8765`. Exercise the catalog, buyer request, supplier agent draft, blocked agent commitment, human approvals, delivery and acceptance. Restart the process to reset synthetic state. Role buttons are explicit simulations, not login. The server binds only to loopback and checks Host, Origin and CSRF tokens. Do not proxy or expose it publicly. No real records should be entered.

HTTP verification: 12 synthetic checks passed, including the complete rework/acceptance flow and rejected CSRF, Origin and Host checks. See [HTTP evidence](evidence/http-check.json). Browser visual verification was unavailable because the browser tool timed out.

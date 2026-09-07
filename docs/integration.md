# Contributor and due diligence integration contract

Upstream reference: https://github.com/AAH20/permissioned-contributor-agent
Due diligence source lineage: https://github.com/AAH20/A2Z_due-diligence-agents

Proposed evidence envelope: engagement ID, requesting organization, purpose, document allowlist, grant expiry, reviewer identity, source URI/hash, finding, exact supporting quote, source timestamp, model/tool versions and uncertainty. A trusted adapter must validate the envelope against current room ACLs and consent before retrieval, then verify its outputs. Never accept an agent's self-declared authorization.

The prior reference includes a real LangGraph synthetic replay and selected due-diligence components with attribution. This marketplace deliberately does not invoke it as a supplier verification service. Its quote checks validate provenance of synthetic findings, not legal, financial or security conclusions. Production integration remains gated on authenticated room grants, reviewed data retention and independent evaluation.

Future graph retrieval must filter by authorized engagement and document before search, then recheck authorization on returned evidence. Graph edges must retain provenance and expiry. LangGraph controls a bounded workflow, not access policy. Pinecone is an optional managed retrieval service, not an OSS dependency or a graph authorization system. A local lexical baseline should precede any vector or GraphRAG investment.

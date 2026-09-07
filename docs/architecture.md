# Architecture and staged implementation

The durable unit is an engagement between a buyer organization and supplier organization. Communities are discovery contexts, not owners of all member data. A user may belong to multiple organizations, with authority evaluated separately. Only explicitly invited suppliers see a request. A submitted proposal is visible to its supplier and buyer. Engagements admit only the contracting organizations. Service listings require explicit public opt-in.

Implemented state sequence: open request, draft proposal, supplier submission, buyer award, active engagement, submitted milestone, acceptance or changes requested. A local acceptance is a reference workflow decision, not a legal signature or payment authorization. No automatic community-to-sales conversion exists.

## Production work before any shared deployment

1. Authenticated identity and session boundary, verified organization ownership, reviewer roles and unforgeable delegated authority. Replace caller-provided human/agent flags with trusted authentication claims and step-up approval.
2. Transactional concurrency controls, idempotency keys, version-bound approvals, multiple milestones, contract versions, change orders, cancellation, disputes and retention/deletion jobs.
3. Tenant-aware SQL policies, encryption, secrets management, dedicated audit storage with payload hashes and independent attestations, backups and restore drills.
4. Web application for opted-in catalog, buyer requests and proposals. Input limits, rate limits, abuse reports, accessibility and security review.
5. Supplier identity/credential verification with scoped access. Evidence expiry and appeals. No global personal trust score.
6. Payment and e-signature provider due diligence, jurisdiction-specific terms, tax/payout handling, reconciliation and human exception review. No escrow claim without an appropriate licensed arrangement.
7. Bounded workers and connector adapters, verified permission provenance, source ACL checks before indexing and retrieval, short retention and consent withdrawal handling.
8. Operational incident response, independent holdout evaluation, external penetration test and community administrator acceptance.

Start with curated community security/governance services. Expand by category only after repeat satisfactory transactions and positive contribution margin. Future procurement workflows for regulated organizations need separate assessments and contracts, not a compliance badge inherited from this pilot.

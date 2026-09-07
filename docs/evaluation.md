# KPIs, evaluation and bounded evolution

Current evidence: deterministic synthetic regression tests and one local engagement replay. No real buyers, revenue, independent holdout, moderation accuracy or production isolation measurement exists. Passing tests does not clear the production gate.

| KPI | Definition | Proposed gate or use |
|---|---|---|
| Unauthorized actions | Successful disallowed operations / attempted disallowed operations | Zero observed; any failure blocks release |
| Tenant leakage | Forbidden records returned / adversarial cross-tenant probes | Zero observed; independent review required |
| Approval integrity | Commitments lacking required human approval / all commitments | Zero |
| Matching precision@5 | Relevant eligible suppliers in top five / five | Target >=0.8 on adjudicated holdout; abstention tracked separately |
| Critical evidence misses | Missed critical facts / labeled critical facts | Zero observed on >=50 independent critical cases |
| Citation support | Supported factual claims / all factual claims | Target 1.0 on >=200 independent cases |
| Request conversion | Awarded qualified requests / all qualified requests in cohort | Baseline first; segment by category |
| Time to proposal | Median and p95 elapsed time to first qualified submitted proposal | Baseline first, including unanswered requests as censored |
| Acceptance | Milestones accepted by due date / milestones due in cohort | Baseline first |
| Repeat purchase | Buyers with another purchase in 90 days / eligible buyer cohort | Measure mature cohorts only |
| Disputes/refunds | Disputed/refunded engagements / completed engagements | Report separately with severity |
| Contribution margin | Revenue less variable payment, hosting, model and support costs | Positive before category expansion |

## Loop engineering

The marketplace state machine is deterministic. No model-driven self-modification ships. Future proposal-only agent loop: retrieve within approved room, generate candidate with provenance, verify, perform at most two repairs, then abstain or request human review. Proposed defaults: top_k=5, graph_hops=1, max_iterations=3, 30-second worker deadline and explicit cost ceiling. These limits are design parameters, not implemented runtime controls in this repository.

Split future datasets by engagement/organization to prevent leakage, with a frozen holdout. Compare a challenger to the deployed baseline on critical failures, quality, latency and cost. Humans approve every configuration release. Never mutate ACLs, consent, write permissions, approval requirements or retention through an evolution loop. Maintain versioned datasets, rollback targets and signed release decisions. Community safety KPIs cannot be traded away for conversion or revenue.

# Research Thrusts — Thematic Companion

*Aaron D. Schroeder, Ph.D. — companion to `research_directions_draft.md`,
2026-05-06.*

This document is the **thematic** view of the research program;
`research_directions_draft.md` is the **strategic** view (federal
programs, tiers, 12-month plan). Read both — they cover different axes.

## Umbrella

**Auditable Agentic AI for Public-Interest Data Production** —
auditability as a structural property of the data-production pipeline,
not a probabilistic property of any single model output. Built so that
LLM-driven datasets can withstand line-by-line audit by statistical
agencies, courts, and regulatory bodies.

## Three thrusts

### Thrust 1 — Multi-Agent Inference Pipelines

Decomposing data-production tasks into typed, testable agent stages
with explicit state, contracts, and reasoning traces.

- **Repos:** `dpi_stdn_agentic`, `dpi_budget_estimation_agentic`,
  `dpi_stdn_development`.
- **Papers:** MEKH Agentic AI technical report; IBES technical report
  (BI-2026-3); HDSR invited *Compressing the Data Science Pipeline*
  (in preparation).

### Thrust 2 — Trust Infrastructure

Workflow-level mechanisms making agentic outputs reliable enough for
official-statistics use: convergence detection, ontology-anchored
normalization, authoritative-data reconciliation, first-class
provenance.

- **Repos:** the convergence/debate machinery inside `dpi_stdn_agentic`
  and `dpi_budget_estimation_agentic`; `ai-knowledge-graph`; `LightRAG`;
  `TheRegistry2`.
- **Published-track gap.** No methods paper yet formalizes the trust
  approach.
- **Forthcoming methods paper.** *Auditable by Construction: A
  Workflow-Level Approach to Trust in LLM Data Pipelines* — target
  HDSR, companion to "Compressing the Pipeline." In active drafting at
  `~/git/dpi_auditable_methods_paper`. Spine: a five-category taxonomy
  of trust mechanisms; contribution: formalizing Category 5
  (workflow-level construction-time trust) with a three-part diagnostic
  (stage commitment, external grounding, composable provenance).

### Thrust 3 — Public-Interest Application Domains

- *Health and social-services access.* Physician + licensed-childcare
  accessibility at the census block group level (VA, NCR); workforce
  indicators.
- *National-security economics.* Classified intelligence-budget
  reconciliation; technology supply-chain dependency mapping.
- **Repos:** `Social-Data-Commons`, `sdc.geographies`,
  `social_data_commons`, `virginia_public_health_data`,
  `national_capital_region_data`, `stdn-explorer`, `lia`, `catchment`.
- **Papers:** two Data & Policy accessibility submissions under review;
  ongoing administrative-data integration work continuing the
  Project Child HANDS / SLDS / Virginia 511 lineage.

## Why the thematic view matters

The strategic doc tells you which agencies to apply to and in what
order. The thematic view tells you what *story* binds the proposals
together — important because Aaron's funding pattern increasingly
benefits from a coordinated 3-proposal slate (NSF NCSES + Census CDE
+ DARPA AIE + NSF Convergence) sharing a single methodological core.
Without the umbrella + thrusts framing, those proposals read as
unrelated; with it, they become variations on a single research
program.

The methods paper effort (Thrust 2) is the most strategically leveraged
single activity right now: it would convert the workflow-level trust
infrastructure from "described in technical reports and enacted in
code" into "published, citable method," which is the missing anchor
for the cross-cutting infrastructure proposals.

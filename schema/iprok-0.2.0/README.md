# IproK 0.2.0 draft: expanded project-control schema

Created 19 October 2026. **Proposed extension**, not a replacement for the preserved published 0.1.0 or a claim of historical study deployment. The canonical integrated distribution for this draft is `ontology.ttl`; equivalent RDF/XML, JSON-LD and N-Triples are provided.

## Scope

This draft contains 138 classes, 271 object properties, 679 datatype properties, 9 annotation properties and 2 generic RDF properties. It includes 21 namespace modules:

| Module | Namespace suffix | Purpose |
|---|---|---|
| Foundation and governance | `iprok#` | Shared concepts, organisations, project membership and governance |
| Schedule and control | `iprok/schedule#` | Published task structure, activities, dependencies, baselines and earned-value snapshots |
| Resources and productivity | `iprok/resource#` | Published resources, workers, crews, skills and measured productivity |
| Cost and rate analysis | `iprok/cost#` | Published cost classification, basic rates, analysis versions and design options |
| Integration | `iprok/integrated#` | Published resource allocations and shared cross-module predicates |
| Measurement and billing | `iprok/billing#` | BOQ, measurements, running-account bills, recoveries and payments |
| Procurement and stores | `iprok/procurement#` | Orders, receipts, issues, vendors and offers |
| Documents and RFIs | `iprok/document#` | Documents, drawings, revisions, annotations, transmittals and RFIs |
| Building models | `iprok/building#` | IFC models, elements, review comments, health checks and member identity |
| Coordination and risk | `iprok/coordination#` | Events, issues, clash batches and risks |
| Quality | `iprok/quality#` | Inspections, checklist items, non-conformances and hold points |
| Safety | `iprok/safety#` | Incidents and incident types |
| Tenders | `iprok/tender#` | Tender records, extracted BOQ, comparisons, recommendations and reference rates |
| External signals | `iprok/signal#` | Weather, material-price, labour and historical weather declarations |
| Site intelligence | `iprok/site#` | Site context, hydrology, logistics, labour, climate, utilities and worker safety |
| Approvals | `iprok/approval#` | Statutory approval records |
| Property inventory | `iprok/property#` | Towers, units and unit types |
| Collections and escrow | `iprok/finance#` | Payment milestones, demands, collections and escrow records |
| Handover | `iprok/handover#` | Handover packages, snags, warranties and defects |
| Reporting and queries | `iprok/reporting#` | Progress reports, photo metadata and saved queries; no media files |
| Activity prediction | `iprok/prediction#` | Activity prediction records; no trained model or performance claim |

All prefixes above are under `https://w3id.org/`, using the registered lowercase `iprok` path. The version IRI is `https://w3id.org/iprok/draft/0.2.0`. The redirect update is submitted separately to the upstream service; use the direct hosted files until that update is merged. The module files in `modules/` are subject-based partitions with their blank-node expressions, intended to be used with the integrated distribution rather than independently closed import graphs.

## Connected integration layer

The draft adds **144 newly authored typed object properties** in the integration namespace. They join all **21 modules into one connected module graph**, spanning **40 distinct cross-module pairs**. The complete class graph is connected when explicit inheritance is included. These additions express new proposed schema design, not retained runtime implementation or historical results.

`relationship-contract.json` defines each property, its domain, range, intended meaning and proposal status. Generic migrated predicates retain their semantics. **75 optional integration shapes** check that newly used links refer to IRIs of the intended class; they do not require historical records to acquire new fields. Constraints on explicit record roles are tested without RDFS inference to avoid letting range inference manufacture a valid target type.

Constructed diagnostics verify 144 valid links, 144 rejected literal targets, 144 rejected wrong-class targets and four cross-module SPARQL paths. The retained-corpus check separately tests the complete combined schema. Select a network line to inspect its properties and distinguish proposed integration links from source declarations.

## Compatibility decisions

- Of the published ontology's 404 non-header assertions, 401 are retained after explicit namespace normalisation and three containment-as-subclass assertions are corrected. `Task`, `WorkPackage` and `WBS_Element` now inherit from `IproKThing`, rather than making tasks and work packages subclasses of Project. Existing containment object properties retain the work-breakdown structure. This correction prevents project-only SHACL constraints being applied to activity records under RDFS inference. Its ontology header is replaced by an explicitly dated draft header in this new distribution. Published source files at the project root are unchanged. Identifiers in the expanded draft use lowercase `https://w3id.org/iprok`; `namespace-migration.json` records 1,330 former draft identifiers, including the former version IRI. No automatic RDF identity or equivalence is claimed.
- The platform `Project` class is deliberately integrated with the existing `schedule:Project` because both describe the construction-project context.
- The source platform `Activity` becomes `schedule:Activity`, a newly declared subclass of the published `schedule:Task`. Their identifiers are not collapsed.
- The source platform `Constraint` becomes `schedule:WorkConstraint`, a newly declared subclass of the published generic `iprok:Constraint`. Its work-readiness fields are not imposed on every generic constraint.
- Published `schedule:plannedStartDate` and `schedule:plannedFinishDate` belong to `TaskTime`. Platform activity dates therefore become `schedule:activityPlannedStartDate` and `schedule:activityPlannedFinishDate`. This avoids silently adding a second domain to a shared predicate.
- Worker, User and Actor remain separate concepts. No unsupported person/resource equivalence is asserted.
- Existing polymorphic predicates keep their original domain/range semantics. Assigning a property to a module via source SHACL usage does **not** create an `rdfs:domain`.
- No `owl:equivalentClass` or `owl:equivalentProperty` mapping is asserted. `dct:source` records lineage, not semantic interchangeability.

## Migration and validation

`mapping.json` records all 1,000 source identifiers and their IproK destinations, ownership decisions and reasons. `shapes.ttl` uses the same identifier map. Full IRIs embedded in the source SPARQL constraint have also been rewritten. Existing instance data must be migrated with this exact map; changing a prefix string is insufficient because terms now occupy several module namespaces.

The source schema comes from platform commit `59bb8c2ae61228cd21778cc6beae523331f4529a`. Both platform ontology files are included. The source schema and original published files remain separately downloadable for comparison. Source wording has been retained where available, with functional component naming. Additional missing definitions are marked as editorial additions in the RDF.

`release.json` records exact counts, partitions and hashes. `validation.json` records dated diagnostics. Validation includes the retained 193-example corpus after consistent IRI migration, graph equivalence across all four distributions, namespace-normalised retention of original assertions, namespace collision checks and constraint-reference checks. A passing corpus is an engineering regression check; it does not establish complete logical consistency, runtime compatibility, an accepted historical release or thesis validity. Legal and source-specific operational comments remain source declarations rather than independently verified legal guidance.

Review the compatibility decisions and missing domain/range declarations before adopting this draft as an application contract. The IprokDoc source release remains separately preserved. The w3id contribution contains only redirect rules and maintainer information; its activation depends on upstream merge.

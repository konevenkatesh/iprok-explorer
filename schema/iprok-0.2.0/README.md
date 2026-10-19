# IproK 0.2.0 draft: expanded project-control schema

Created 19 October 2026. **Proposed extension**, not a replacement for the preserved published 0.1.0 or a claim of historical study deployment. The canonical integrated distribution for this draft is `ontology.ttl`; equivalent RDF/XML, JSON-LD and N-Triples are provided.

## Scope

This draft contains 138 classes, 127 object properties, 679 datatype properties, 9 annotation properties and 2 generic RDF properties. It includes 21 namespace modules:

| Module | Namespace suffix | Purpose |
|---|---|---|
| Foundation and governance | `IproK#` | Shared concepts, organisations, project membership and governance |
| Schedule and control | `IproK/schedule#` | Published task structure, activities, dependencies, baselines and earned-value snapshots |
| Resources and productivity | `IproK/resource#` | Published resources, workers, crews, skills and measured productivity |
| Cost and rate analysis | `IproK/cost#` | Published cost classification, basic rates, analysis versions and design options |
| Integration | `IproK/integrated#` | Published resource allocations and shared cross-module predicates |
| Measurement and billing | `IproK/billing#` | BOQ, measurements, running-account bills, recoveries and payments |
| Procurement and stores | `IproK/procurement#` | Orders, receipts, issues, vendors and offers |
| Documents and RFIs | `IproK/document#` | Documents, drawings, revisions, annotations, transmittals and RFIs |
| Building models | `IproK/building#` | IFC models, elements, review comments, health checks and member identity |
| Coordination and risk | `IproK/coordination#` | Events, issues, clash batches and risks |
| Quality | `IproK/quality#` | Inspections, checklist items, non-conformances and hold points |
| Safety | `IproK/safety#` | Incidents and incident types |
| Tenders | `IproK/tender#` | Tender records, extracted BOQ, comparisons, recommendations and reference rates |
| External signals | `IproK/signal#` | Weather, material-price, labour and historical weather declarations |
| Site intelligence | `IproK/site#` | Site context, hydrology, logistics, labour, climate, utilities and worker safety |
| Approvals | `IproK/approval#` | Statutory approval records |
| Property inventory | `IproK/property#` | Towers, units and unit types |
| Collections and escrow | `IproK/finance#` | Payment milestones, demands, collections and escrow records |
| Handover | `IproK/handover#` | Handover packages, snags, warranties and defects |
| Reporting and queries | `IproK/reporting#` | Progress reports, photo metadata and saved queries; no media files |
| Activity prediction | `IproK/prediction#` | Activity prediction records; no trained model or performance claim |

All prefixes above are under `https://w3id.org/`. These are draft IRIs; persistent resolution for the new paths has not been registered. Download the schema from this project directly. The module files in `modules/` are subject-based partitions with their blank-node expressions, intended to be used with the integrated distribution rather than independently closed import graphs.

## Compatibility decisions

- Of the published ontology's 404 non-header assertions, 401 remain intact and three containment-as-subclass assertions are corrected. `Task`, `WorkPackage` and `WBS_Element` now inherit from `IproKThing`, rather than making tasks and work packages subclasses of Project. Existing containment object properties retain the work-breakdown structure. This correction prevents project-only SHACL constraints being applied to activity records under RDFS inference. Its ontology header is replaced by an explicitly dated draft header in this new distribution. Published files at the project root are unchanged.
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

`release.json` records exact counts, partitions and hashes. `validation.json` records dated diagnostics. Validation includes the retained 193-example corpus after consistent IRI migration, graph equivalence across all four distributions, original assertion preservation, namespace collision checks and constraint-reference checks. A passing corpus is an engineering regression check; it does not establish complete logical consistency, runtime compatibility, an accepted historical release or thesis validity. Legal and source-specific operational comments remain source declarations rather than independently verified legal guidance.

Review the compatibility decisions and missing domain/range declarations before adopting this draft as an application contract. The existing w3id redirect configuration and IprokDoc release have not been altered.

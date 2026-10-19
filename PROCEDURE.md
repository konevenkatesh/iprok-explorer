# Source, verification and publication procedure

## Proposed IproK extension

The user requested rewriting and extending IproK on 19 October 2026. The new `schema/iprok-0.2.0/` distribution includes 138 classes across 21 namespaces, 127 object properties and 679 datatype properties. The atlas defaults to this draft. Original IproK and the unchanged Niyoj source snapshot remain selectable. `mapping.json` records the 1,000-identifier migration; `release.json` records counts, hashes, three hierarchy corrections and compatibility choices. See the extension README for the full contract.

Run `python scripts/extend_iprok.py` before rebuilding the explorer, and `python scripts/verify_extended.py` after generation. Run the retained SHACL corpus against consistently migrated fixtures before reporting conformance. Do not change ontology, shapes or fixtures while that validation is running.

## Keep the schema and its explanation separate

The source ontology defines classes and properties. A populated knowledge graph would contain actual project records conforming to those meanings. This website publishes a visual explanation of the schema; it contains no historical case-study dataset and makes no prediction-performance claim.

Published IproK contains 28 classes, 22 object properties, 39 data properties and 9 annotation properties, with 420 explicit triples. Its five internal namespace groups are shared foundation, schedule, resource, cost and integrated. Nine external annotation terms are grouped separately as metadata. The published source does not declare a building-model module.

Labels are taken from source when present; otherwise the display label is derived from the IRI. Ninety-three declared terms lack a source comment. Editorial guides explain supported relationships without adding axioms or pretending that a missing source definition exists.

The network's solid arrows use explicit object-property domains and ranges; dashed arrows use explicit `rdfs:subClassOf` declarations. Domain and range are RDFS inference semantics, not mandatory-field validation. Multiple domains or ranges are not alternatives. The class hierarchy view is declared hierarchy only, not a reasoner output. Isolated nodes are retained. Force arrangement, cluster placement and colours are presentation choices. Conceptual module membership follows namespace, not a new OWL module axiom.

## Retain consistent sources

1. Obtain an identified source commit. Preserve exact source namespaces and metadata.
2. Keep historical IproK separate from later BIMSaarthi/Niyoj development. No automatic term renaming or equivalence claim is permitted.
3. For Niyoj, take `bs.ttl`, `iprok_site_intelligence.ttl` and `shapes.ttl` from the same commit. The extension must be explicitly loaded with the core; the core does not import it. The current retained snapshot is identified in `schema/niyoj/source.json`.
4. Run `python scripts/build_schema.py`. This creates term indexes, relationship edges and source hashes. It aligns the downloadable N-Triples graph to Turtle while preserving the previous export in `legacy/`. RDF/XML and JSON-LD already agree with the retained Turtle source.
5. Run `python scripts/verify_schema.py` and `node --check assets/explorer.js`. Check actual source assertions, graph equivalence, source hashes, declaration counts, all four guided paths, constructed query results and local interface links.
6. Inspect desktop and narrow-screen rendering. Exercise concept focus, module focus, arrangements, drag/pan/zoom, term inspector, filters, source switching, forward/inverse connection paths and disconnected classes. Record limitations honestly.

The Niyoj module overview uses 20 explicitly editorial functional groups covering all 111 classes. The original five-module source is still selectable. The checked source has explicit domains on only 13 of 105 object properties; no `sh:class` property constraint is declared in SHACL. The class-to-class network therefore deliberately omits undeclared links; absence of an edge does not establish absence of a runtime connection. Domain-free predicates may be intentional.

The Niyoj schema audit covers 111 classes, 105 object properties, 640 data properties and 2 RDF properties across 2,946 explicit core/extension triples. SHACL is a separate file. Runtime coverage is not the entire planned architecture; a stale source version header is not evidence of a complete semantic release. Import closure, OWL consistency, application behaviour and historical research validation require separate checks.

## Publish this separate GitHub project

1. Commit this repository to `konevenkatesh/iprok-explorer`.
2. Enable GitHub Pages with GitHub Actions as its source.
3. Push to `main`. The workflow verifies schema assets before packaging only website files and deploying.
4. Wait for a successful Pages deployment and verify the returned public URL, data files and source-download links.
5. Preserve the current IprokDoc repository and w3id redirects. This separate explanatory site does not change persistent identifiers or canonical ontology IRIs.

## If the persistent identifier is updated later

The current upstream w3id repository places entries under `ids/iprok/`; the older fork used `iprok/`. The upstream accepts redirect rules and brief maintainer information, not ontology or interface files. Publish content to the target before changing redirects and submit a reviewed pull request against upstream. Test the rules with the upstream checker and a real Apache server.

The inspected deployed base URL always redirects to HTML, even when an RDF Accept header is supplied. Existing version-shaped URLs also redirect to unversioned latest files; they should not be described as immutable releases. The source ontology's uppercase `IproK` namespace differs from the lowercase `iprok` PURL. These findings are recorded for a later, separately scoped redirect change. No current identifier has been rewritten or repurposed here.

## Verification evidence

The release manifest records source hashes and declaration audits. `data/verification.json` records the actual checks completed for this website, including the dated Niyoj conformance check. Constructed diagnostics are engineering checks performed on 19 October 2026, not historical thesis evidence. No project-level empirical result is inferred from schema counts or a passing example corpus.

# IproK visual schema atlas

An independent, static website for understanding the Integrated Project Knowledge ontology. Network diagrams are generated from retained RDF declarations, with labelled editorial explanations and source inspection.

## Expanded IproK draft

The default view is the proposed **IproK 0.2.0** extension: **21 namespace modules, 138 classes, 271 object properties and 679 data properties**. It rewrites the platform schema into IproK module identifiers while preserving the published release separately. A full mapping, migrated SHACL constraints, four RDF formats and module partitions are available in `schema/iprok-0.2.0/`. Three containment-as-subclass errors are explicitly corrected in the draft. See its [specification](schema/iprok-0.2.0/README.md).

## Explore

- **Network atlas:** drag nodes, pan and zoom, focus a module or a concept, follow its neighbours and inspect assertions. Module clusters, connected network, radial and class hierarchy arrangements use the same schema.
- **Expanded module map:** 20 editorial functional groups covering all 111 Niyoj runtime classes, with source-supported cross-group links and class drill-down.
- **Module walkthrough:** shared foundation, schedule, resources, cost and integration, with the exact declared relationships.
- **Guided paths:** work breakdown, resource allocation, allocation cost and task dependencies.
- **Connection finder:** a shortest object-property path between two classes, including marked inverse steps, and a corresponding SPARQL pattern.
- **Reference explorer:** searchable cards, table and graph; complete per-term assertions and linked source files.
- **Source selector:** published IproK and a separate, commit-pinned Niyoj runtime snapshot. These are separate vocabularies with no asserted equivalence mapping.

## Run locally

```sh
python3 -m http.server 8873
```

Open `http://localhost:8873/`. Fetching the schema requires HTTP rather than `file://`.

## Verify and rebuild

```sh
python3 -m pip install -r requirements.txt
python3 scripts/extend_iprok.py
python3 scripts/build_schema.py
python3 scripts/verify_schema.py
python3 scripts/verify_extended.py
node --check assets/explorer.js
```

The GitHub Pages workflow verifies declarations before deployment. No server, API key, telemetry, project-instance dataset or photograph is required.

See [PROCEDURE.md](PROCEDURE.md) for publication, provenance, audit limitations and the separate w3id contribution procedure.

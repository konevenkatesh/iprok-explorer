# IproK visual schema atlas

An independent, static website for understanding the Integrated Project Knowledge ontology. Network diagrams are generated from retained RDF declarations, with labelled editorial explanations and source inspection.

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
python3 scripts/build_schema.py
python3 scripts/verify_schema.py
node --check assets/explorer.js
```

The GitHub Pages workflow verifies declarations before deployment. No server, API key, telemetry, project-instance dataset or photograph is required.

See [PROCEDURE.md](PROCEDURE.md) for publication, provenance, audit limitations and the separate w3id contribution procedure.

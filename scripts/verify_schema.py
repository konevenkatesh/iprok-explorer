"""Check actual RDF, generated indexes, provenance, guided paths and local assets."""
import hashlib, json, re
from pathlib import Path
from urllib.parse import urlparse, unquote
from rdflib import Graph, RDF, OWL, RDFS, URIRef
from rdflib.compare import isomorphic
from rdflib.plugins.sparql.parser import parseQuery
ROOT=Path(__file__).resolve().parents[1]
g=Graph().parse(ROOT/'ontology.ttl',format='turtle')
for name,fmt in [('ontology.owl','xml'),('ontology.nt','nt'),('ontology.jsonld','json-ld')]:
 assert isomorphic(g,Graph().parse(ROOT/name,format=fmt)),f'{name} is not equivalent to Turtle'
manifest=json.loads((ROOT/'data/manifest.json').read_text())
for release in manifest['datasets']:
 data=json.loads((ROOT/'data'/f"{release['id']}.json").read_text()); union=Graph()
 for source in release['files']:
  p=ROOT/source['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256'],p
  union.parse(p,format='turtle')
 assert len(union)==data['audit']['triples']
 for typ,label in [(OWL.Class,'Class'),(OWL.ObjectProperty,'Object property'),(OWL.DatatypeProperty,'Data property')]:
  assert len(set(union.subjects(RDF.type,typ)))==data['audit']['counts'][label],label
 ids={t['id'] for t in data['terms']}
 for term in data['terms']:
  assert len(term['statements'])==len(list(union.predicate_objects(URIRef(term['id'])))),term['id']
  assert all((ROOT/f).is_file() for f in term['sourceFiles'])
 for edge in data['edges']:
  assert edge['source'] in ids and edge['target'] in ids
  if edge['property']:
   assert (URIRef(edge['property']),RDFS.domain,URIRef(edge['source'])) in union
   assert (URIRef(edge['property']),RDFS.range,URIRef(edge['target'])) in union
  else:assert (URIRef(edge['source']),RDFS.subClassOf,URIRef(edge['target'])) in union
group_data=json.loads((ROOT/'data/niyoj-modules.json').read_text());niyoj=json.loads((ROOT/'data/niyoj.json').read_text());grouped=[c for m in group_data['groups'] for c in m['classes']];assert len(grouped)==len(set(grouped))==111;assert set(grouped)=={t['local'] for t in niyoj['terms'] if t['kind']=='Class'}
source=json.loads((ROOT/'schema/niyoj/source.json').read_text())
for filename,sha in source['files'].items():assert hashlib.sha256((ROOT/'schema/niyoj'/filename).read_bytes()).hexdigest()==sha
# All four editorial journeys use exact declared object-property chains.
js=(ROOT/'assets/explorer.js').read_text()
iprok=json.loads((ROOT/'data/iprok.json').read_text());by_name={t['local']:t for t in iprok['terms']}
chains=re.findall(r"chain:\[([^]]+)\]",js)
assert len(chains)==4
for chain in chains:
 names=re.findall(r"'([^']+)'",chain)
 for a,p,b in zip(names[0::2],names[1::2],names[2::2]):
  prop=by_name[p];assert by_name[a]['id'] in prop['domain'] and by_name[b]['id'] in prop['range'],(a,p,b)
# Exercise generated forward and inverse SPARQL against constructed diagnostics.
s=Graph();ns='https://example.org/constructed/'
for a,p,b in [('Task','taskHasResourceAllocation','ResourceAllocation'),('ResourceAllocation','allocationAssignsResource','Resource')]:
 sa,sb=URIRef(ns+a),URIRef(ns+b)
 s.add((sa,RDF.type,URIRef(by_name[a]['id'])));s.add((sb,RDF.type,URIRef(by_name[b]['id'])));s.add((sa,URIRef(by_name[p]['id']),sb))
for reverse in [False,True]:
 query=f"SELECT * WHERE {{ ?t a <{by_name['Task']['id']}> . ?t <{by_name['taskHasResourceAllocation']['id']}> ?a . ?a <{by_name['allocationAssignsResource']['id']}> ?r . ?r a <{by_name['Resource']['id']}> . }}"
 if reverse:query=f"SELECT ?node0 ?node1 ?node2 WHERE {{ ?node0 a <{by_name['Resource']['id']}> . ?node1 <{by_name['allocationAssignsResource']['id']}> ?node0 . ?node2 <{by_name['taskHasResourceAllocation']['id']}> ?node1 . ?node2 a <{by_name['Task']['id']}> . }}"
 parseQuery(query);assert len(list(s.query(query)))==1
# Validate all direct local links used by the new interface (the preserved legacy is archival).
for filename in ['index.html','main.html']:
 html=(ROOT/filename).read_text()
 for href in re.findall(r'(?:href|src)="([^"]+)"',html):
  path=urlparse(href)
  if not path.scheme and path.path:assert (ROOT/unquote(path.path)).is_file(),href
assert (ROOT/'index.html').read_bytes()==(ROOT/'main.html').read_bytes()
print('PASS: four RDF formats, source hashes, both schema indexes, complete term assertions, declared edges, four guided paths, constructed query diagnostics and interface assets.')

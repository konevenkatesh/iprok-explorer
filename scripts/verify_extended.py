"""Verify the proposed extension without claiming OWL consistency or runtime adoption."""
import json,hashlib
from pathlib import Path
from rdflib import Graph,URIRef,RDF,RDFS,OWL,Namespace,Literal,BNode
from rdflib.compare import isomorphic
from rdflib.plugins.sparql.parser import parseQuery
R=Path(__file__).resolve().parents[1];p=R/'schema/iprok-0.2.0';IP='https://w3id.org/iprok';BS='https://bimsaarthi.com/ontology/v0/';DCT=Namespace('http://purl.org/dc/terms/');SH=Namespace('http://www.w3.org/ns/shacl#')
g=Graph().parse(p/'ontology.ttl');base=Graph().parse(R/'ontology.ttl');source=Graph().parse(R/'schema/niyoj/bs.ttl');source.parse(R/'schema/niyoj/iprok_site_intelligence.ttl');s=Graph().parse(p/'shapes.ttl');mapping=json.loads((p/'mapping.json').read_text());m={t['source']:t['iprok'] for t in mapping['terms']};release=json.loads((p/'release.json').read_text())
assert len(set(m.values()))==len(m)==1000
ns=json.loads((p/'namespace-migration.json').read_text());nm={x['previous']:x['canonical'] for x in ns['identifiers']};assert ns['canonicalNamespace']==IP and len(nm)==1330
assert nm['https://w3id.org/IproK/0.2.0']==IP+'/draft/0.2.0'
assert all(v.startswith(IP) for v in nm.values())
for f,sha in release['files'].items():assert hashlib.sha256((p/f).read_bytes()).hexdigest()==sha,f
for f,fmt in [('ontology.owl','xml'),('ontology.jsonld','json-ld'),('ontology.nt','nt')]:assert isomorphic(g,Graph().parse(p/f,format=fmt)),f
legacy=Graph();legacy+=base;base=Graph()
for triple in legacy:base.add(tuple(URIRef(str(x).replace('https://w3id.org/IproK',IP)) if isinstance(x,URIRef) and str(x).startswith('https://w3id.org/IproK') else x for x in triple))
corrections={(URIRef(IP+'/schedule#'+a),RDFS.subClassOf,URIRef(IP+'/schedule#'+b)) for a,b in [('Task','WBS_Element'),('WorkPackage','WBS_Element'),('WBS_Element','Project')]}
preserved=[t for t in base if t[0]!=URIRef(IP) and t not in corrections]
assert all(t not in g for t in corrections)
assert all(t in g for t in preserved if not any(isinstance(x,BNode) for x in t)) and len(preserved)==401
ba=Graph();bb=Graph()
for t in preserved:
 if any(isinstance(x,BNode) for x in t):ba.add(t)
for t in g:
 if any(isinstance(x,BNode) for x in t):bb.add(t)
assert isomorphic(ba,bb)
contract=json.loads((p/'relationship-contract.json').read_text())['relations']
for typ,count in [(OWL.Class,138),(OWL.ObjectProperty,127+len(contract)),(OWL.DatatypeProperty,679)]:assert len(set(g.subjects(RDF.type,typ)))==count
# Domain/range transformation is exact, not inferred from property usage.
for predicate in [RDFS.domain,RDFS.range]:
 for a,_,b in source.triples((None,predicate,None)):
  assert (URIRef(m.get(str(a),str(a))),predicate,URIRef(m.get(str(b),str(b)))) in g
for graph in [g,s]:
 for a,b,c in graph:
  assert not str(a).startswith(BS) and not str(b).startswith(BS)
  if isinstance(c,URIRef) and str(c).startswith(BS):assert b==DCT.source,(a,b,c)
for graph in [g,s]:
 for triple in graph:
  assert all(not isinstance(x,URIRef) or not str(x).startswith('https://w3id.org/IproK') for x in triple)
assert (URIRef(IP),OWL.versionIRI,URIRef(IP+'/draft/0.2.0')) in g
for query in s.objects(None,SH.select):
 assert BS not in str(query);parseQuery(str(query).replace('$this','?this'))
assert m[BS+'plannedStartDate']==IP+'/schedule#activityPlannedStartDate'
assert (URIRef(IP+'/schedule#Activity'),RDFS.subClassOf,URIRef(IP+'/schedule#Task')) in g
assert (URIRef(IP+'/schedule#WorkConstraint'),RDFS.subClassOf,URIRef(IP+'#Constraint')) in g
assert not list(g.triples((None,OWL.equivalentClass,None))) and not list(g.triples((None,OWL.equivalentProperty,None)))
assert len(list((p/'modules').glob('*.ttl')))==21
# Every authored relation has its intended single domain/range and an optional typed shape.
for relation in contract:
 prop=URIRef(relation['property']);assert set(g.objects(prop,RDFS.domain))=={URIRef(relation['source'])};assert set(g.objects(prop,RDFS.range))=={URIRef(relation['target'])}
 assert any(s.value(shape,SH.path)==prop and s.value(shape,SH['class'])==URIRef(relation['target']) for shape in s.subjects(SH.path,prop))
# All classes form one connected component when explicit inheritance is included.
from collections import defaultdict
adj=defaultdict(set);classes=set(g.subjects(RDF.type,OWL.Class))
for prop in g.subjects(RDF.type,OWL.ObjectProperty):
 for a in g.objects(prop,RDFS.domain):
  for b in g.objects(prop,RDFS.range):
   if a in classes and b in classes:adj[a].add(b);adj[b].add(a)
for a,b in g.subject_objects(RDFS.subClassOf):
 if a in classes and b in classes:adj[a].add(b);adj[b].add(a)
seen=set();pending=[URIRef(IP+'/schedule#Project')]
while pending:
 node=pending.pop()
 if node in seen:continue
 seen.add(node);pending.extend(adj[node]-seen)
assert seen==classes,classes-seen
for f in (p/'modules').glob('*.ttl'):
 module=Graph().parse(f)
 for ext,fmt in [('owl','xml'),('jsonld','json-ld'),('nt','nt')]:assert isomorphic(module,Graph().parse(f.with_suffix('.'+ext),format=fmt)),str(f)
from functools import lru_cache
from collections import Counter
def shape_signature(graph):
 @lru_cache(None)
 def value(node):
  if isinstance(node,URIRef):return ('iri',str(node))
  if not isinstance(node,BNode):return ('literal',node.n3())
  return ('blank',tuple(sorted((str(pred),value(obj)) for pred,obj in graph.predicate_objects(node))))
 return len(graph),Counter((str(subject),str(pred),value(obj)) for subject,pred,obj in graph if not isinstance(subject,BNode))
for ext,fmt in [('owl','xml'),('jsonld','json-ld'),('nt','nt')]:assert shape_signature(s)==shape_signature(Graph().parse(p/('shapes.'+ext),format=fmt))
print('PASS: proposed IproK extension counts, 21 partitions, 1,000-identifier injective mapping, 401 namespace-normalised retained assertions and 3 explicit hierarchy corrections, exact domain/range migration, constraint query IRIs and four equivalent RDF distributions.')

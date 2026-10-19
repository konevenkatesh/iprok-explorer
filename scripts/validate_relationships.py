"""Constructed diagnostics for the new optional typed relationship layer.

These are newly dated engineering examples, not project observations.
"""
import json,sys
from pathlib import Path
from collections import defaultdict
from rdflib import Graph,URIRef,BNode,Literal,RDF,RDFS,OWL,Namespace
from rdflib.plugins.sparql.parser import parseQuery
from pyshacl import validate
R=Path(__file__).resolve().parents[1];P=R/'schema/iprok-0.2.0';SH=Namespace('http://www.w3.org/ns/shacl#');IP='https://w3id.org/iprok'
contract=json.loads((P/'relationship-contract.json').read_text())['relations'];full=Graph().parse(P/'shapes.ttl');schema=Graph().parse(P/'ontology.ttl');shapes=Graph()
# Isolate the new integration shapes so examples do not impersonate complete project records.
for node in full.subjects(RDF.type,SH.NodeShape):
 if str(node).startswith(IP+'/shapes#Integration'):
  pending=[node];seen=set()
  while pending:
   n=pending.pop()
   if n in seen:continue
   seen.add(n)
   for p,o in full.predicate_objects(n):
    shapes.add((n,p,o))
    if isinstance(o,BNode):pending.append(o)
valid=invalid_literal=invalid_type=0
for i,r in enumerate(contract):
 a=URIRef('urn:iprok:constructed:subject');b=URIRef('urn:iprok:constructed:object');prop=URIRef(r['property']);data=Graph();data.add((a,RDF.type,URIRef(r['source'])));data.add((b,RDF.type,URIRef(r['target'])));data.add((a,prop,b))
 ok,_,report=validate(data,shacl_graph=shapes,inference='none');assert ok,(r['label'],report);valid+=1
 wrong_literal=Graph();wrong_literal+=data;wrong_literal.remove((a,prop,b));wrong_literal.add((a,prop,Literal('not an object record')))
 ok,_,_=validate(wrong_literal,shacl_graph=shapes,inference='none');assert not ok,r['label'];invalid_literal+=1
 wrong_type=Graph();wrong_type+=data;wrong_type.remove((b,RDF.type,URIRef(r['target'])));wrong_type.add((b,RDF.type,OWL.Thing))
 ok,_,_=validate(wrong_type,shacl_graph=shapes,inference='none');assert not ok,r['label'];invalid_type+=1
# Confirm module connectivity and useful multi-module answer paths on a constructed graph.
classes={str(c) for c in schema.subjects(RDF.type,OWL.Class)};module=lambda iri:iri.split('#')[0].rsplit('/',1)[-1];adj=defaultdict(set);nodes=set(module(c) for c in classes);pairs=set()
for prop in schema.subjects(RDF.type,OWL.ObjectProperty):
 for a in schema.objects(prop,RDFS.domain):
  for b in schema.objects(prop,RDFS.range):
   if str(a) in classes and str(b) in classes:
    ma,mb=module(str(a)),module(str(b))
    if ma!=mb:adj[ma].add(mb);adj[mb].add(ma);pairs.add(tuple(sorted([ma,mb])))
seen=set();pending=['schedule']
while pending:
 n=pending.pop()
 if n in seen:continue
 seen.add(n);pending.extend(adj[n]-seen)
assert seen==nodes and len(nodes)==21
example=Graph();lookup={r['label']:r for r in contract}
paths=[['projectHasActivity','activityHasBOQItem','boqHasRateAnalysis'],['projectHasActivity','activityLinkedElement'],['projectHasActivity','activityHasProductivityObservation','observationUsesCrew'],['projectHasDocument']]
query_count=0
for path_index,path in enumerate(paths):
 triples=[]
 for i,name in enumerate(path):
  r=lookup[name];a=URIRef(f'urn:iprok:constructed:{path_index}:{i}');b=URIRef(f'urn:iprok:constructed:{path_index}:{i+1}');example.add((a,URIRef(r['property']),b));triples.append(f'?v{i} <{r["property"]}> ?v{i+1} .')
 query='SELECT * WHERE { '+' '.join(triples)+' }';parseQuery(query);assert list(example.query(query));query_count+=1
result={'checkedOn':'2026-10-19','type':'New constructed relationship diagnostics; not historical research evidence','relations':len(contract),'validTypedExamplesAccepted':valid,'literalTargetsRejected':invalid_literal,'wrongClassTargetsRejected':invalid_type,'validationInference':'none, to check explicit record roles without RDFS range inference manufacturing target types','moduleNodes':len(nodes),'moduleConnectedComponents':1,'crossModulePairs':len(pairs),'crossModuleQueryExamples':query_count,'scope':'Integration shapes only for constructed examples; the separate retained-corpus run checks the combined schema and shapes'}
(P/'relationship-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

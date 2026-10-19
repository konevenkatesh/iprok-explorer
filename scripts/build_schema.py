"""Generate the explorer from retained RDF sources; never infer term equivalence."""
import hashlib, json, re
from pathlib import Path
from collections import Counter
from rdflib import Graph, RDF, RDFS, OWL, URIRef, BNode, Literal, Namespace
from rdflib.compare import isomorphic
ROOT = Path(__file__).resolve().parents[1]
SH = Namespace('http://www.w3.org/ns/shacl#')
TYPES = [(OWL.Class,'Class'),(RDFS.Class,'Class'),(OWL.ObjectProperty,'Object property'),(OWL.DatatypeProperty,'Data property'),(OWL.AnnotationProperty,'Annotation property'),(RDF.Property,'Property')]
def short(s):
 s=str(s); return s.rsplit('#',1)[-1] if '#' in s else s.rstrip('/').rsplit('/',1)[-1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build(key, files, name, note):
 g=Graph(); file_subjects={}
 for f in files:
  part=Graph().parse(ROOT/f,format='turtle'); g+=part; file_subjects[f]=set(part.subjects())
 kinds={}
 for typ,label in reversed(TYPES):
  for s in g.subjects(RDF.type,typ):
   if isinstance(s,URIRef): kinds[str(s)]=label
 terms=[]
 for uri,kind in sorted(kinds.items()):
  s=URIRef(uri)
  labels=sorted(str(x) for x in g.objects(s,RDFS.label))
  statements=[]
  def value(o,seen=None):
   if isinstance(o,BNode):
    seen=set() if seen is None else seen
    if o in seen:return {'value':'[recursive expression]','type':'expression'}
    return {'value':' ; '.join(short(p)+' '+value(v,seen|{o})['value'] for p,v in sorted(g.predicate_objects(o),key=lambda t:(str(t[0]),str(t[1])))), 'type':'expression'}
   return {'value':str(o),'type':'iri' if isinstance(o,URIRef) else 'literal','language':getattr(o,'language',None),'datatype':str(o.datatype) if isinstance(o,Literal) and o.datatype else None}
  for p,o in sorted(g.predicate_objects(s),key=lambda t:(str(t[0]),str(t[1]))): statements.append({'predicate':str(p),**value(o)})
  module=uri.split('#')[0].rstrip('/').rsplit('/',1)[-1]
  if uri.startswith('https://bimsaarthi.com/ontology/v0/'): module='BIMSaarthi v0'
  elif uri.startswith('https://w3id.org/iprok#'): module='IproK'
  elif not uri.startswith(('https://w3id.org/IproK','https://w3id.org/iprok')): module='External metadata'
  terms.append({'id':uri,'local':short(uri),'label':labels[0] if labels else re.sub(r'(?<=[a-z])(?=[A-Z])',' ',short(uri)).replace('_',' '),'declaredLabel':bool(labels),'kind':kind,'module':module,'description':' '.join(str(x) for x in g.objects(s,RDFS.comment)), 'domain':[str(x) for x in g.objects(s,RDFS.domain)],'range':[str(x) for x in g.objects(s,RDFS.range)],'parents':[str(x) for x in g.objects(s,RDFS.subClassOf) if isinstance(x,URIRef)],'statements':statements,'sourceFiles':[f for f in files if s in file_subjects[f]]})
 priority={'Class':0,'Object property':1,'Data property':2,'Property':3,'Annotation property':4}
 terms.sort(key=lambda t:(priority[t['kind']],t['module'],t['label'].lower()))
 edges=[]
 for t in terms:
  for parent in t['parents']:
   if parent in kinds:edges.append({'source':t['id'],'target':parent,'label':'subclass of','property':None})
  if t['kind']=='Object property':
   for d in t['domain']:
    for r in t['range']:
     if d in kinds and r in kinds:edges.append({'source':d,'target':r,'label':t['local'],'property':t['id'],'proposed':any('Newly proposed IproK integration relationship' in x['value'] for x in t['statements']),'definition':t['description']})
 counts=Counter(kinds.values())
 audit={'triples':len(g),'declaredTerms':len(terms),'counts':dict(counts),'missingLabels':[t['id'] for t in terms if not t['declaredLabel']], 'missingComments':[t['id'] for t in terms if not t['description']], 'propertiesWithoutDomain':[t['id'] for t in terms if 'property' in t['kind'].lower() and not t['domain']], 'propertiesWithoutRange':[t['id'] for t in terms if 'property' in t['kind'].lower() and not t['range']], 'scope':'Static declaration audit. Missing domains may be intentional for polymorphic predicates. No OWL reasoner, import closure or historical study validation is claimed.'}
 out={'id':key,'name':name,'note':note,'files':[{'path':f,'sha256':digest(ROOT/f)} for f in files],'terms':terms,'edges':edges,'audit':audit}
 (ROOT/'data'/f'{key}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 return out,g
iprok,g=build('iprok',['ontology.ttl'],'IproK · published 0.1.0','Retained published ontology. Namespace case is significant: https://w3id.org/IproK#. Module IRIs are preserved.')
# Generate matching representations from the existing Turtle source; original files are retained in legacy/.
for name,fmt in [('ontology.nt','nt'),('ontology.owl','xml'),('ontology.jsonld','json-ld')]:
 current=Graph().parse(ROOT/name,format=fmt)
 if not isomorphic(g,current):
  g.serialize(ROOT/name,format=fmt)
 assert isomorphic(g,Graph().parse(ROOT/name,format=fmt)),name
outputs=[iprok]
if (ROOT/'schema/iprok-0.2.0/ontology.ttl').exists():
 expanded,eg=build('expanded',['schema/iprok-0.2.0/ontology.ttl'],'IproK · expanded 0.2.0 draft','Proposed IproK extension using canonical lowercase https://w3id.org/iprok; historical files remain separately preserved. Created 19 October 2026; engineering verification is separate from historical thesis results.')
 es=Graph().parse(ROOT/'schema/iprok-0.2.0/shapes.ttl',format='turtle')
 expanded['audit']['shaclTriples']=len(es)
 expanded['audit']['nodeShapes']=len(set(es.subjects(RDF.type,SH.NodeShape)))
 expanded['shapes']=[{'id':str(n),'targets':[str(x) for x in es.objects(n,SH.targetClass)],'properties':[{'path':str(es.value(b,SH.path)),'constraints':[{'predicate':str(k),'value':str(v)} for k,v in es.predicate_objects(b)]} for b in es.objects(n,SH.property)]} for n in sorted(set(es.subjects(RDF.type,SH.NodeShape)),key=str)]
 (ROOT/'data/expanded.json').write_text(json.dumps(expanded,ensure_ascii=False,indent=2)+'\n')
 names={'IproK':'Foundation & governance','schedule':'Schedule & control','resource':'Resources & productivity','cost':'Cost & rate analysis','integrated':'Integration','billing':'Measurement & billing','procurement':'Procurement & stores','document':'Documents & RFIs','building':'Building models','coordination':'Coordination & risk','quality':'Quality & hold points','safety':'Safety','tender':'Tender intelligence','signal':'External signals','site':'Site intelligence','approval':'Statutory approvals','property':'Property inventory','finance':'Collections & escrow','handover':'Handover & defects','reporting':'Field reporting & queries','prediction':'Activity prediction'}
 palette=['#54776b','#37785e','#6c63a0','#b17b36','#a46e42','#7e8e41','#4a799c','#347f8b','#9c687d','#5a8c79','#bd704f','#887445','#718e9d','#4e9582','#8b7caa','#847ba7','#a58b42','#7f9063','#718aa0','#8a688e','#5a938d']
 mods=sorted(set(t['module'] for t in expanded['terms'] if t['kind']=='Class'))
 (ROOT/'data/expanded-modules.json').write_text(json.dumps({'basis':'Namespace modules in the proposed expanded IproK schema. Explicit domain/range cross-module links only.','groups':[{'id':mod,'name':names.get(mod,mod),'classes':[t['local'] for t in expanded['terms'] if t['kind']=='Class' and t['module']==mod],'colour':palette[i%len(palette)]} for i,mod in enumerate(mods)]},indent=2)+'\n')
 outputs.append(expanded)
p=ROOT/'schema/niyoj/source.json'
if p.exists():
 source=json.loads(p.read_text())
 out,ng=build('niyoj',['schema/niyoj/bs.ttl','schema/niyoj/iprok_site_intelligence.ttl'],'Niyoj · dated source snapshot','Subsequent platform development. Separate namespace; no owl:equivalentClass or owl:equivalentProperty mapping to IproK is asserted. The source header still declares 0.1.0 / M1 subset; this is not a new semantic release.')
 out['source']=source
 shapes=Graph().parse(ROOT/'schema/niyoj/shapes.ttl',format='turtle')
 out['audit']['shaclTriples']=len(shapes)
 out['audit']['nodeShapes']=len(set(shapes.subjects(RDF.type,SH.NodeShape)))
 out['shapes']=[{'id':str(s),'targets':[str(x) for x in shapes.objects(s,SH.targetClass)],'properties':[{'path':str(shapes.value(b,SH.path)), 'constraints': [{'predicate':str(k),'value':str(v)} for k,v in shapes.predicate_objects(b)]} for b in shapes.objects(s,SH.property)]} for s in sorted(set(shapes.subjects(RDF.type,SH.NodeShape)),key=str)]
 (ROOT/'data/niyoj.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');outputs.append(out)
manifest={'generatedOn':'2026-10-19','scope':'Schema declarations only. No project records, credentials or experimental results.','datasets':[{'id':o['id'],'name':o['name'],'note':o['note'],'files':o['files'],'audit':o['audit']} for o in outputs]}
(ROOT/'data/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({o['id']:o['audit']['counts']|{'triples':o['audit']['triples']} for o in outputs},indent=2))

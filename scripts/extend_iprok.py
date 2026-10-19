"""Build a proposed IproK extension from retained sources, with an explicit IRI map.

Namespace ownership is editorial organisation, not a new domain assertion.
"""
import json,re,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from rdflib import Graph,URIRef,BNode,Literal,Namespace,RDF,RDFS,OWL,XSD
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'schema/iprok-0.2.0';OUT.mkdir(parents=True,exist_ok=True)
BS='https://bimsaarthi.com/ontology/v0/';IP='https://w3id.org/IproK';SH=Namespace('http://www.w3.org/ns/shacl#');DCT=Namespace('http://purl.org/dc/terms/');VANN=Namespace('http://purl.org/vocab/vann/')
base=Graph().parse(ROOT/'ontology.ttl');source=Graph().parse(ROOT/'schema/niyoj/bs.ttl');source.parse(ROOT/'schema/niyoj/iprok_site_intelligence.ttl');shapes=Graph().parse(ROOT/'schema/niyoj/shapes.ttl');groups=json.loads((ROOT/'data/niyoj-modules.json').read_text())['groups']
namespace={'governance':IP+'#','planning':IP+'/schedule#','resources':IP+'/resource#','estimating':IP+'/cost#','billing':IP+'/billing#','procurement':IP+'/procurement#','documents':IP+'/document#','models':IP+'/building#','coordination':IP+'/coordination#','quality':IP+'/quality#','safety':IP+'/safety#','tenders':IP+'/tender#','signals':IP+'/signal#','site':IP+'/site#','approvals':IP+'/approval#','inventory':IP+'/property#','collections':IP+'/finance#','handover':IP+'/handover#','reporting':IP+'/reporting#','prediction':IP+'/prediction#','shared':IP+'/integrated#'}
class_owner={BS+c:m['id'] for m in groups for c in m['classes']};owners=defaultdict(Counter)
for prop,_,domain in source.triples((None,RDFS.domain,None)):
 if str(domain) in class_owner:owners[str(prop)][class_owner[str(domain)]]+=1
# SHACL usage establishes a navigation owner, but never manufactures an RDFS domain.
for shape,_,target in shapes.triples((None,SH.targetClass,None)):
 owner=class_owner.get(str(target))
 if not owner:continue
 pending=[shape];seen=set()
 while pending:
  node=pending.pop()
  if node in seen:continue
  seen.add(node)
  for p,o in shapes.predicate_objects(node):
   if p==SH.path and isinstance(o,URIRef) and str(o).startswith(BS):owners[str(o)][owner]+=1
   if isinstance(o,BNode):pending.append(o)
classes=set(source.subjects(RDF.type,OWL.Class));props=set()
for typ in [OWL.ObjectProperty,OWL.DatatypeProperty,RDF.Property,OWL.AnnotationProperty]:props.update(source.subjects(RDF.type,typ))
node_shapes=set(shapes.subjects(RDF.type,SH.NodeShape));mapping={};ownership={};reasons={}
all_iris={str(x) for graph in [source,shapes] for triple in graph for x in triple if isinstance(x,URIRef) and str(x).startswith(BS)}
for old in sorted(all_iris):
 name=old[len(BS):];node=URIRef(old)
 if node in node_shapes:
  new=IP+'/shapes#'+name;owner='shapes';reason='SHACL node shape, separate shape namespace'
 elif old in class_owner:
  owner=class_owner[old];new=namespace[owner]+name;reason='Class functional group from source declaration and comment'
  if name=='Project':new=IP+'/schedule#Project';reason='Intentional reuse of the published project class; construction-project scope preserved'
  if name=='Constraint':new=IP+'/schedule#WorkConstraint';reason='Distinct work-readiness record, kept separate from the published generic Constraint'
 else:
  used=set(owners[old])
  owner=next(iter(used)) if len(used)==1 else 'shared'
  new=namespace[owner]+name;reason='Single module usage in explicit domain / SHACL target' if len(used)==1 else ('Shared across modules; domain semantics preserved' if used else 'No scoped ownership declaration; retained in integration namespace')
  if node not in props:reason='Named schema value / supporting node; retained as a schema identifier'
 # Never silently merge a new declaration with an old one just because a label matches.
 if URIRef(new) in set(base.subjects()) and name!='Project':
  new=namespace.get(owner,namespace['shared'])+('activity'+name[0].upper()+name[1:] if node in props else name+'Record');reason+='; disambiguated from a published IproK term'
 mapping[old]=new;ownership[old]=owner;reasons[old]=reason
assert len(set(mapping.values()))==len(mapping),'IRI collision'
def rewrite(x):
 if isinstance(x,URIRef):return URIRef(mapping.get(str(x),str(x)))
 if isinstance(x,Literal):
  text=str(x)
  # Explicit IRIs embedded in the retained SPARQL constraint must follow the IRI map.
  for old in sorted(mapping,key=len,reverse=True):
   text=text.replace('<'+old+'>','<'+mapping[old]+'>')
  text=re.sub(r'\bbs:([A-Za-z_][A-Za-z0-9_-]*)',lambda m:'<'+mapping.get(BS+m[1],namespace['shared']+m[1])+'>',text)
  return Literal(text,lang=x.language,datatype=x.datatype)
 return x
new=Graph()
for t in base:
 if t[0]!=URIRef(IP):new.add(t)
for s,p,o in source:
 if s in set(source.subjects(RDF.type,OWL.Ontology)):continue
 new.add((rewrite(s),rewrite(p),rewrite(o)))
newsh=Graph()
for s,p,o in shapes:newsh.add((rewrite(s),rewrite(p),rewrite(o)))
# New editorial definitions are explicit release changes, never attributed to the historical source.
for term in set(new.subjects(RDF.type,OWL.Class))|set(new.subjects(RDF.type,OWL.ObjectProperty))|set(new.subjects(RDF.type,OWL.DatatypeProperty)):
 name=str(term).rsplit('#',1)[-1]
 if not list(new.objects(term,RDFS.label)):
  new.add((term,RDFS.label,Literal(re.sub(r'(?<=[a-z])(?=[A-Z])',' ',name).replace('_',' '),lang='en')))
 if not list(new.objects(term,RDFS.comment)):
  kind='class' if (term,RDF.type,OWL.Class) in new else 'property'
  domains=[str(o).rsplit('#',1)[-1] for o in new.objects(term,RDFS.domain)];ranges=[str(o).rsplit('#',1)[-1] for o in new.objects(term,RDFS.range)]
  definition=f"The {re.sub(r'(?<=[a-z])(?=[A-Z])',' ',name).lower()} {kind} in the integrated project information model."
  if kind=='property' and domains and ranges:definition+=' Its declared domain is '+', '.join(domains)+' and its declared range is '+', '.join(ranges)+'.'
  new.add((term,RDFS.comment,Literal(definition,lang='en')));new.add((term,DCT.description,Literal('Editorial definition added for proposed IproK 0.2.0; inspect the retained source and mapping record.',lang='en')))
# Improve source-derived definitions without carrying promotional implementation claims into the draft.
class_guides={'Actor':'A person or organisational actor to whom scheduled work can be assigned.','Calendar':'A definition of working and non-working periods used to interpret scheduled work.','Constraint':'A condition restricting the execution or organisation of project work.','IproKThing':'The common parent class for the published IproK project-information concepts.','CostCategory':'A classification grouping cost items by their purpose or accounting category.','CostItem':'A cost record associated with scheduled work or a resource allocation.','CostType':'A classification of expenditure by the kind of resource or expense involved.','EquipmentCost':'A cost-type classification for equipment-related expenditure.','ExpenseItem':'A cost-type classification for other project expenses.','LaborCost':'A cost-type classification for labour-related expenditure.','MaterialCost':'A cost-type classification for material-related expenditure.','Resource':'A resource available for allocation to a task or activity.','ResourceType':'A classification describing the kind of a resource.','EquipmentResource':'A resource-type classification for equipment.','LaborResource':'A resource-type classification for labour.','MaterialResource':'A resource-type classification for materials.','UserDefinedResource':'A resource-type classification defined for a project-specific need.','ResourceConstraint':'A condition restricting the availability or use of a resource.','ResourceAllocation':'An assignment record connecting scheduled work, an allocated resource and an associated cost item.','TrackingTag':'An identifier concept used to track a resource.','Units':'A unit of measure used to express a resource quantity.','Project':'The construction-project context in which work, records and control decisions are organised.','Task':'A unit of scheduled work within a project.','TaskDependency':'A relationship record describing precedence between scheduled tasks.','TaskTime':'A time record associated with a scheduled task.','WBS_Element':'An element of the work breakdown structure used to organise tasks.','WorkPackage':'A grouping of project work represented in the work breakdown structure.','Milestone':'A task representing a significant scheduled event or control point.'}
for name,definition in class_guides.items():
 for subject in list(new.subjects(RDF.type,OWL.Class)):
  if str(subject).rsplit('#',1)[-1]==name and not list(base.objects(subject,RDFS.comment)):
   new.set((subject,RDFS.comment,Literal(definition,lang='en')))
overrides={'JointMeasurement':'A joint measurement record supporting separate contractor and departmental sign-off roles.','ActivityPrediction':'A versioned record describing an activity-level prediction and its input, model and baseline provenance.','Incident':'A recorded site safety event with its severity, activity context and follow-up information.','Organisation':'An organisation owning project records and defining a tenant boundary.','User':'An authenticated platform user, such as a site engineer, quality controller or project manager.'}
for old,destination in mapping.items():
 subject=URIRef(destination)
 if URIRef(old) in classes:
  comments=list(new.objects(subject,RDFS.comment))
  for comment in comments:
   text=overrides.get(old[len(BS):],str(comment))
   if 'This is the first software implementation' in text:text=text.split('This is the first software implementation')[0].strip()
   text=text.replace(' — ','; ')
   if text!=str(comment):new.remove((subject,RDFS.comment,comment));new.add((subject,RDFS.comment,Literal(text,lang=comment.language,datatype=comment.datatype)))
# Use functional component names in the proposed public vocabulary; preserve exact source files separately.
for s,p,o in list(new):
 if isinstance(o,Literal) and p in [RDFS.comment,RDFS.label]:
  text=str(o).replace('NIYOJ','project information interface').replace('Niyoj','project information interface').replace('BIMSaarthi','IproK framework')
  if text!=str(o):new.remove((s,p,o));new.add((s,p,Literal(text,lang=o.language,datatype=o.datatype)))
root=URIRef(IP);version=URIRef(IP+'/0.2.0')
for triple in [(root,RDF.type,OWL.Ontology),(root,DCT.title,Literal('Integrated Project Knowledge (IproK) ontology: expanded project-control schema',lang='en')),(root,OWL.versionIRI,version),(root,OWL.versionInfo,Literal('0.2.0-draft')),(root,DCT.created,Literal('2026-10-19',datatype=XSD.date)),(root,DCT.creator,Literal('Venkatesh Kone')),(root,DCT.contributor,Literal('Prof. Gangadhar Mahesh')),(root,DCT.license,URIRef('https://creativecommons.org/licenses/by/4.0/')),(root,DCT.description,Literal('Proposed expansion of the published IproK ontology using retained platform schema declarations. Original identifiers are preserved. Schema validation is dated engineering verification, not historical thesis evidence.',lang='en')),(root,DCT.source,URIRef('https://github.com/konevenkatesh/IprokDoc/tree/ee4cf206af08a47db3363fa4404ac51cce1868de')),(root,VANN.preferredNamespacePrefix,Literal('iprok')),(root,VANN.preferredNamespaceUri,Literal(IP+'#'))]:new.add(triple)
for imp in [URIRef('http://www.w3.org/ns/prov'),URIRef('http://www.w3.org/2006/time'),URIRef('http://www.opengis.net/ont/geosparql')]:new.add((root,OWL.imports,imp))
# Correct containment modelled as inheritance; existing object properties retain containment.
corrected_hierarchy=[('Task','WBS_Element'),('WorkPackage','WBS_Element'),('WBS_Element','Project')]
for child,parent in corrected_hierarchy:
 new.remove((URIRef(IP+'/schedule#'+child),RDFS.subClassOf,URIRef(IP+'/schedule#'+parent)))
 new.add((URIRef(IP+'/schedule#'+child),RDFS.subClassOf,URIRef(IP+'#IproKThing')))
# These are explicit compatibility choices, not inferred equivalences.
new.add((URIRef(IP+'/schedule#Activity'),RDFS.subClassOf,URIRef(IP+'/schedule#Task')))
new.add((URIRef(IP+'/schedule#WorkConstraint'),RDFS.subClassOf,URIRef(IP+'#Constraint')))
for old,newuri in mapping.items():
 if URIRef(old) in classes|props:
  new.add((URIRef(newuri),DCT.source,URIRef(old)))
  new.add((URIRef(newuri),DCT.isPartOf,URIRef(namespace.get(ownership[old],namespace['shared']).split('#')[0])))
# Authored integration layer: dedicated typed properties, leaving generic source predicates unchanged.
contract_path=OUT/'relationship-contract.json'
proposed_relations=json.loads(contract_path.read_text())['relations'] if contract_path.exists() else []
relation_shapes={}
for relation in proposed_relations:
 prop=URIRef(relation['property']);domain=URIRef(relation['source']);range_=URIRef(relation['target'])
 assert not list(new.predicate_objects(prop)), 'New integration predicate collides with an existing declaration: '+str(prop)
 assert (domain,RDF.type,OWL.Class) in new and (range_,RDF.type,OWL.Class) in new
 for t in [(prop,RDF.type,OWL.ObjectProperty),(prop,RDFS.domain,domain),(prop,RDFS.range,range_),(prop,RDFS.label,Literal(re.sub(r'(?<=[a-z])(?=[A-Z])',' ',relation['label']),lang='en')),(prop,RDFS.comment,Literal(relation['definition'],lang='en')),(prop,DCT.description,Literal(relation['status']+'. '+relation['basis'],lang='en')),(prop,DCT.created,Literal('2026-10-19',datatype=XSD.date)),(prop,RDFS.isDefinedBy,version),(prop,DCT.isPartOf,URIRef(IP+'/integrated'))]:new.add(t)
 # Optional when absent; an authored link, when present, must point to an IRI of its declared target class.
 if domain not in relation_shapes:
  shape=URIRef(IP+'/shapes#Integration'+str(domain).rsplit('#',1)[-1]+'Shape');relation_shapes[domain]=shape
  newsh.add((shape,RDF.type,SH.NodeShape));newsh.add((shape,SH.targetClass,domain))
 shape=relation_shapes[domain];ps=BNode();newsh.add((shape,SH.property,ps));newsh.add((ps,SH.path,prop));newsh.add((ps,SH.nodeKind,SH.IRI));newsh.add((ps,SH['class'],range_));newsh.add((ps,SH.message,Literal('Proposed integration link must reference an IRI typed as '+str(range_).rsplit('#',1)[-1]+'.',lang='en')))
for graph in [new,newsh]:
 graph.bind('iprok',IP+'#');graph.bind('schedule',IP+'/schedule#');graph.bind('resource',IP+'/resource#');graph.bind('cost',IP+'/cost#');graph.bind('integrated',IP+'/integrated#');graph.bind('sh',SH);graph.bind('dct',DCT)
new.serialize(OUT/'ontology.ttl',format='turtle');new.serialize(OUT/'ontology.owl',format='xml');new.serialize(OUT/'ontology.jsonld',format='json-ld');new.serialize(OUT/'ontology.nt',format='nt');newsh.serialize(OUT/'shapes.ttl',format='turtle')
# Partition the integrated graph by subject namespace; blank-node expressions follow their subject.
modules_dir=OUT/'modules';modules_dir.mkdir(exist_ok=True)
module_stats=[]
for prefix in sorted({str(s).split('#')[0] for s in new.subjects() if isinstance(s,URIRef) and str(s).startswith(IP) and '#' in str(s)}):
 subset=Graph();roots={s for s in new.subjects() if isinstance(s,URIRef) and str(s).startswith(prefix+'#')};queue=list(roots);seen=set()
 while queue:
  s=queue.pop()
  if s in seen:continue
  seen.add(s)
  for p,o in new.predicate_objects(s):
   subset.add((s,p,o))
   if isinstance(o,BNode):queue.append(o)
 name=prefix.rsplit('/',1)[-1] if prefix!=IP else 'core';subset.serialize(modules_dir/(name+'.ttl'),format='turtle');module_stats.append({'module':name,'namespace':prefix+'#','triples':len(subset),'classes':len(set(subset.subjects(RDF.type,OWL.Class)))})
records=[{'source':old,'iprok':mapping[old],'owner':ownership[old],'basis':reasons[old]} for old in sorted(mapping)]
(OUT/'mapping.json').write_text(json.dumps({'status':'Proposed namespace migration, not an owl:equivalentClass/equivalentProperty alignment','sourceCommit':'59bb8c2ae61228cd21778cc6beae523331f4529a','rules':['Published IproK identifiers preserved','Project deliberately reused','Activity added as a subclass of published Task','WorkConstraint kept distinct and added as a subclass of generic Constraint','No new property domains inferred from usage or SHACL','Source SPARQL IRIs rewritten consistently with the explicit map','Corrected Task/WorkPackage/WBS containment-as-subclass assertions to IproKThing; containment remains expressed by object properties'],'terms':records},indent=2)+'\n')
summary={'status':'0.2.0-draft; proposed expansion created 19 October 2026','triples':len(new),'classes':len(set(new.subjects(RDF.type,OWL.Class))),'objectProperties':len(set(new.subjects(RDF.type,OWL.ObjectProperty))),'dataProperties':len(set(new.subjects(RDF.type,OWL.DatatypeProperty))),'proposedTypedLinks':len(proposed_relations),'integrationShapes':len(relation_shapes),'shapeTriples':len(newsh),'mappedIdentifiers':len(mapping),'modules':module_stats,'preservedPublishedAssertions':sum(1 for t in base if t[0]!=URIRef(IP) and t in new),'correctedHierarchy':[{'removed':f'schedule:{a} rdfs:subClassOf schedule:{b}','added':f'schedule:{a} rdfs:subClassOf iprok:IproKThing'} for a,b in corrected_hierarchy],'newCompatibilityAxioms':['schedule:Activity rdfs:subClassOf schedule:Task','schedule:WorkConstraint rdfs:subClassOf iprok:Constraint'],'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in OUT.iterdir() if f.is_file() and f.name!='release.json'}}
(OUT/'release.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k not in ['files','modules']},indent=2))

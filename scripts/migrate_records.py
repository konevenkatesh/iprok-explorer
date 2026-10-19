"""Migrate known schema identifiers in an RDF file without changing source records in place.

Uses explicit namespace/platform maps. Unknown instance identifiers and literal values are retained.
"""
import argparse,json
from pathlib import Path
from rdflib import Graph,URIRef
ROOT=Path(__file__).resolve().parents[1];SCHEMA=ROOT/'schema/iprok-0.2.0'
def identifier_map():
 ns=json.loads((SCHEMA/'namespace-migration.json').read_text())['identifiers']
 platform=json.loads((SCHEMA/'mapping.json').read_text())['terms']
 return {**{x['previous']:x['canonical'] for x in ns},**{x['source']:x['iprok'] for x in platform}}
def migrate_graph(source):
 mapping=identifier_map();output=Graph();changed=0;unknown=set()
 for triple in source:
  values=[]
  for value in triple:
   if isinstance(value,URIRef) and str(value) in mapping:
    replacement=URIRef(mapping[str(value)]);changed+=replacement!=value;values.append(replacement)
   else:
    if isinstance(value,URIRef) and str(value).startswith('https://w3id.org/IproK'):unknown.add(str(value))
    values.append(value)
  output.add(tuple(values))
 return output,{'inputTriples':len(source),'outputTriples':len(output),'changedIRIOccurrences':changed,'unmappedUppercaseIRIs':sorted(unknown),'scope':'Known schema identifiers only; instance identifiers and literals retained unless explicitly present in a migration map.'}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',type=Path);parser.add_argument('output',type=Path);parser.add_argument('--format',default='turtle');args=parser.parse_args()
 if args.input.resolve()==args.output.resolve():parser.error('Use a separate output file; original records must be preserved.')
 if args.output.exists():parser.error('Output already exists; choose a new revision path.')
 result,report=migrate_graph(Graph().parse(args.input));result.serialize(args.output,format=args.format);print(json.dumps(report,indent=2))
if __name__=='__main__':main()

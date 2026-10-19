"""Exercise proposed IproK rules against a running Apache; does not change the live PURL."""
import argparse,json,hashlib
from pathlib import Path
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
formats=[('text/turtle','ttl'),('application/rdf+xml','owl'),('application/ld+json','jsonld'),('application/n-triples','nt')]
BASE='https://konevenkatesh.github.io/iprok-explorer';DRAFT=BASE+'/schema/iprok-0.2.0'
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',default='http://127.0.0.1:8894');parser.add_argument('--output',type=Path,default=ROOT/'data/w3id-redirect-test.json');args=parser.parse_args();cases=[]
 def add(path,accept,target,status=303):cases.append((path,accept,target,status))
 for prefix in ['', 'draft/0.2.0']:
  for trail in ['', '/']:
   path='/iprok/'+prefix+trail if prefix else '/iprok/'
   for accept,ext in formats:add(path,accept,DRAFT+'/ontology.'+ext)
   add(path,'text/html',BASE+'/');add(path,'*/*',BASE+'/')
  for accept,ext in formats:add('/iprok/'+(prefix+'/' if prefix else '')+'shapes',accept,DRAFT+'/shapes.'+ext)
  for ext in ['ttl','owl','jsonld','nt']:
   for file in ['ontology','shapes']:add('/iprok/'+(prefix+'/' if prefix else '')+file+'.'+ext,'*/*',DRAFT+'/'+file+'.'+ext)
  for module in sorted(f.stem for f in (ROOT/'schema/iprok-0.2.0/modules').glob('*.ttl')):
   url='/iprok/'+(prefix+'/' if prefix else '')+module
   for accept,ext in formats:add(url,accept,DRAFT+'/modules/'+module+'.'+ext)
   add(url,'text/html',BASE+'/?module='+('IproK' if module=='core' else module))
   for ext in ['ttl','owl','jsonld','nt']:
    for stem in [module,'modules/'+module]:add('/iprok/'+(prefix+'/' if prefix else '')+stem+'.'+ext,'*/*',DRAFT+'/modules/'+module+'.'+ext)
 for accept,ext in formats:add('/iprok/0.1.0/',accept,BASE+'/ontology.'+ext)
 add('/iprok/0.1.0','text/html',BASE+'/?source=iprok')
 for version in ['1.0','99.3.7']:
  for accept,ext in formats:add('/iprok/'+version,accept,'https://konevenkatesh.github.io/IprokDoc/ontology.'+ext)
  add('/iprok/'+version,'text/html','https://konevenkatesh.github.io/IprokDoc/main.html')
 for unknown in ['unknown-module','draft/9.9.9','schedule/UnknownPath']:add('/iprok/'+unknown,'text/html',None,404)
 add('/iprok/.htaccess','text/html',None,403)
 opener=build_opener(NoRedirect());failures=[]
 for path,accept,target,status in cases:
  try:response=opener.open(Request(args.base+path,method='HEAD',headers={'Accept':accept}),timeout=10)
  except HTTPError as error:response=error
  actual=response.status;location=response.headers.get('Location');response.close()
  if actual!=status or target is not None and location!=target:failures.append({'path':path,'accept':accept,'expectedStatus':status,'actualStatus':actual,'expectedLocation':target,'actualLocation':location})
 result={'checkedOn':'2026-10-19','scope':'Local real Apache with upstream w3id configuration; live upstream merge is a separate event','server':'Installed macOS Apache, exact temporary copy of identifier rules and upstream rootless configuration','cases':len(cases),'matched':len(cases)-len(failures),'failures':failures,'ruleFileSHA256':hashlib.sha256((ROOT.parent/'11_IproK_Persistent_ID/ids/iprok/.htaccess').read_bytes()).hexdigest()}
 args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert not failures
if __name__=='__main__':main()

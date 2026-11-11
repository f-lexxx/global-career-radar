import json, re, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'sources.json').read_text())
KEYWORDS=[x.lower() for x in CFG['keywords']]
COUNTRIES=['ghana','nigeria','kenya','south africa','united kingdom','uk','ireland','germany','france','netherlands','switzerland','canada','united states','usa','australia','new zealand','uae','united arab emirates','saudi arabia','singapore','india','poland','spain','portugal','sweden','norway','denmark']

def get_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'GlobalCareerRadar/1.0 (public job board reader)','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=25) as r:return json.loads(r.read().decode('utf-8','replace'))
def clean(s):return re.sub(r'<[^>]+>',' ',s or '').replace('&nbsp;',' ').replace('&amp;','&').strip()
def country_from(text):
    t=(text or '').lower()
    for c in COUNTRIES:
        if c in t:return 'Ghana' if c=='ghana' else c.title()
    if 'remote' in t and any(x in t for x in ['worldwide','anywhere','global','emea','americas']):return 'Global'
    return 'Not stated'
def mode_from(text):
    t=(text or '').lower()
    if any(x in t for x in ['hybrid','partially remote']):return 'Hybrid'
    if any(x in t for x in ['fully remote','remote-first','remote position','work remotely','remote -','remote,','remote (']):return 'Remote'
    if 'remote' in t and any(x in t for x in ['anywhere','global','worldwide']):return 'Remote'
    if any(x in t for x in ['on-site','onsite','in office','office-based']):return 'Onsite'
    return 'Not stated'
def relocation_from(text):
    t=(text or '').lower()
    if re.search(r'no relocation|relocation (?:is )?not (?:available|provided|offered)|unable to provide relocation',t):return 'Not offered'
    if re.search(r'relocation (?:assistance|package|support|allowance)|relocation provided|we will relocate|relocation offered',t):return 'Offered'
    return 'Not stated'
def seniority(title,desc):
    t=(title+' '+desc[:1200]).lower()
    if any(x in t for x in ['chief ','vice president','vp ','director','head of','principal','distinguished']):return 'Lead / Executive'
    if any(x in t for x in ['senior','staff ','lead ','manager','architect']):return 'Senior'
    if any(x in t for x in ['junior','graduate','entry level','intern']):return 'Entry'
    return 'Mid'
def relevant(title,desc):
    t=(title+' '+desc).lower()
    return any(k in t for k in KEYWORDS)
def normalize(company,title,location,description,url,posted,source):
    desc=clean(description)
    blob=' '.join([location or '',desc[:5000]])
    country=country_from(blob)
    mode=mode_from(' '.join([location or '',desc[:5000],title]))
    if country=='Global' and mode=='Not stated':mode='Remote'
    return {'id':re.sub(r'[^a-z0-9]+','-',(company+'-'+title+'-'+url).lower()).strip('-')[:160],
      'title':clean(title),'company':company,'location':clean(location) or 'Location not stated','country':country,
      'work_mode':mode,'relocation':relocation_from(desc),'seniority':seniority(title,desc),
      'description':desc[:1800],'url':url,'posted_at':posted,'source_name':source,
      'verified_at':datetime.now(timezone.utc).isoformat()}

jobs=[];checked=0;errors=[]
for src in CFG.get('greenhouse',[]):
    try:
        data=get_json('https://boards-api.greenhouse.io/v1/boards/'+src['token']+'/jobs?content=true');checked+=1
        for j in data.get('jobs',[]):
            content=j.get('content','');title=j.get('title','')
            if relevant(title,clean(content)):
                jobs.append(normalize(src['name'],title,j.get('location',{}).get('name',''),content,j.get('absolute_url',''),j.get('updated_at',''),src['name']+' official Greenhouse board'))
    except Exception as e:errors.append(src['name']+': '+str(e)[:160])
for src in CFG.get('lever',[]):
    try:
        data=get_json('https://api.lever.co/v0/postings/'+src['site']+'?mode=json');checked+=1
        for j in data if isinstance(data,list) else []:
            title=j.get('text','');cats=j.get('categories',{});loc=cats.get('location','') or cats.get('allLocations','')
            desc=' '.join([clean(j.get('description','')),clean(j.get('descriptionPlain','')),clean(j.get('additional',''))])
            if relevant(title,desc):
                jobs.append(normalize(src['name'],title,loc,desc,j.get('hostedUrl',''),datetime.fromtimestamp(j['createdAt']/1000,timezone.utc).isoformat() if j.get('createdAt') else '',src['name']+' official Lever board'))
    except Exception as e:errors.append(src['name']+': '+str(e)[:160])
# Keep only direct official ATS application URLs and deduplicate.
seen=set();out=[]
for j in jobs:
    if not j['url'].startswith(('https://boards.greenhouse.io/','https://job-boards.greenhouse.io/','https://jobs.lever.co/')):continue
    if j['id'] in seen:continue
    seen.add(j['id']);out.append(j)
out.sort(key=lambda x:x.get('posted_at') or '',reverse=True)
payload={'updated_at':datetime.now(timezone.utc).isoformat(),'sources_checked':checked,'source_errors':errors,'jobs':out}
(ROOT/'data'/'jobs.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False))
print(f'Checked {checked} official boards; saved {len(out)} matching vacancies; {len(errors)} source errors.')

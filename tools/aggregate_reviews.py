"""Aggregate returned exports, one latest rating per respondent/item. Standard library only."""
from pathlib import Path
from datetime import datetime
import argparse,csv,json,statistics,sys
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--output',type=Path,default=Path('ratings_merged.csv'));args=p.parse_args()
data=json.loads((Path(__file__).resolve().parents[1]/'docs/data.json').read_text());items={x['id']:x for x in data['items']};merged={};errors=[];files=sorted(args.directory.glob('*.json'))
if not files:sys.exit('No JSON files found; no output written.')
for path in files:
 try:
  raw=json.loads(path.read_text());assert raw['dataset']==data['dataset'] and raw['dataset_sha256']==data['dataset_sha256'],'Dataset/version mismatch'
  who=raw['respondent_id'];assert isinstance(who,str) and who,'Missing respondent_id'
  pending=[]
  for id,r in raw['reviews'].items():
   assert id in items,'Unknown item';score=r.get('humor_score');assert score is None or type(score)==int and 1<=score<=10,'Invalid score'
   assert r.get('content_sha256')==items[id]['content_sha256'],'Item content mismatch'
   assert r.get('mechanism_error') in ['是','否'] and r.get('explanation_complete') in ['是','否'],'Invalid check'
   stamp=datetime.fromisoformat(r['updated_at'].replace('Z','+00:00'));assert stamp.tzinfo is not None,'Missing timezone';assert isinstance(r.get('note',''),str),'Invalid note'
   pending.append(((who,id),stamp,r))
  for key,stamp,r in pending:
   if key not in merged or stamp>merged[key][0]:merged[key]=(stamp,r)
 except (AssertionError,KeyError,ValueError,TypeError) as e:errors.append(f'{path.name}: {e}')
if errors:sys.exit('No output written. Fix rejected files:\n'+'\n'.join(errors))
def safe(s):return "'"+s if isinstance(s,str) and s.startswith(('=','+','-','@','\t','\r')) else s
def write(path,rows,fields):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:safe(r.get(k,'')) for k in fields} for r in rows)
details=[dict(respondent_id=who,id=id,**r) for (who,id),(_,r) in sorted(merged.items())];summary=[]
for id,x in items.items():
 rr=[r for (_,rid),(_,r) in merged.items() if rid==id];scores=[r['humor_score'] for r in rr if r.get('humor_score') is not None]
 summary.append(dict(id=id,domain=x['domain_zh'],batch=x['batch'],humor_rating_count=len(scores),humor_mean=round(statistics.mean(scores),4) if scores else '',humor_median=statistics.median(scores) if scores else '',annotation_count=len(rr),mechanism_error_yes_count=sum(r.get('mechanism_error')=='是' for r in rr),explanation_incomplete_count=sum(r.get('explanation_complete')=='否' for r in rr)))
write(args.output,summary,['id','domain','batch','humor_rating_count','humor_mean','humor_median','annotation_count','mechanism_error_yes_count','explanation_incomplete_count']);detail=args.output.with_name(args.output.stem+'_details.csv');write(detail,details,['respondent_id','id','humor_score','mechanism_error','explanation_complete','note','updated_at','content_sha256']);print(f'{len(files)} files, {len({k[0] for k in merged})} respondents; wrote {args.output} and {detail}')

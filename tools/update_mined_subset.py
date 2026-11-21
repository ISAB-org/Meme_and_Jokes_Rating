import hashlib, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
BASE = ROOT.parent / 'transfer_1113_analysis' / 'tech-humor-benchmark'
pkg = BASE / '1119_first100_plus_scored_gem'
first = json.loads((pkg / 'items.json').read_text())
first_texts = {x.get('text','').strip() for x in first if x.get('added_human_score') is None}
hist = json.loads((BASE.parent / 'classification_sources' / '02_历史已入选913条逐条.jsonl').read_text())
gem = json.loads((pkg / 'scored_gem_58.json').read_text())['items']

def public_hist(r):
    o = r['original_record']; text = o.get('joke_text','')
    raw = ' '.join(str(o.get(k,'')) for k in ('category','domain','source_url')).lower()
    cat = '铁路' if any(k in raw for k in ('铁路','railway','train')) else ('航空' if any(k in raw for k in ('航空','aviation','airline','aircraft')) else ('苏联' if any(k in raw for k in ('苏联','soviet','ussr')) else ('知乎回答' if '知乎' in raw or 'zhihu' in raw else '其他领域')))
    media = o.get('local_media') or []; image = None
    if media:
        image = 'images/' + Path(media[0].get('local_path','')).name
        src = Path(media[0].get('local_path','')); dst = OUT / image
        if src.exists() and not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
    return {'id': r['id'], 'original_id': r['id'], 'legacy_gem_id': r['id'],
        'domain_id': cat, 'domain_zh': o.get('domain') or '其他挖掘',
        'batch': '后续挖掘（均分≥7，待人工复核）', 'title': text[:80],
        'original_text': text, 'translation_zh': text if o.get('language') != 'en' else '',
        'translation_status': '待人工复核', 'image_path': image,
        'organizer_context': o.get('caveat',''), 'explanation': o.get('why_funny',''),
        'required_knowledge': o.get('required_knowledge',''), 'content_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'source': {'url': o.get('source_url',''), 'limitation': o.get('caveat','')}, 'points': [],
        'mechanism_tags_suggested': [], 'human_score': float(o.get('humor_mean')), 'review_status': '未人工复核'}

def public_gem(x):
    text=x.get('original_text') or x.get('text','')
    image = None
    raw_images = x.get('image_paths') or []
    if raw_images:
        src = pkg / raw_images[0]
        if not src.exists():
            src = Path(raw_images[0])
        if src.exists():
            image = 'images/' + src.name
            dst = OUT / image
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists(): shutil.copy2(src, dst)
    raw = ' '.join(str(x.get(k,'')) for k in ('domain_id','subdomain','group','source')).lower()
    cat = '铁路' if any(k in raw for k in ('铁路','railway','train')) else ('航空' if any(k in raw for k in ('航空','aviation','airline','aircraft')) else ('苏联' if any(k in raw for k in ('苏联','soviet','ussr')) else ('知乎回答' if '知乎' in raw or 'zhihu' in raw else '其他领域')))
    return {'id': x['id'], 'original_id': x.get('original_id',x['id']), 'legacy_gem_id': x.get('legacy_gem_id',x['id']),
        'domain_id': cat, 'domain_zh': x.get('subdomain') or x.get('group','其他'),
        'batch': 'GEM后续挖掘（评分≥7，待人工复核）', 'title': x.get('title',text[:80]),
        'original_text': text, 'translation_zh': x.get('translation_zh',''), 'translation_status': x.get('translation_status','待人工复核'),
        'image_path': image, 'organizer_context': x.get('organizer_context',''),
        'explanation': x.get('explanation',''), 'required_knowledge': x.get('required_knowledge',''),
        'content_sha256': x.get('content_sha256',''), 'source': x.get('source',{}), 'points': [],
        'mechanism_tags_suggested': x.get('mechanism_current','').split('；') if x.get('mechanism_current') else [],
        'human_score': x.get('added_human_score'), 'review_status': '未人工复核'}

rows=[]; seen=set()
for r in hist:
    o=r['original_record']; text=o.get('joke_text','').strip()
    if float(o.get('humor_mean') or 0) < 7 or text in first_texts or r['id'] in seen: continue
    rows.append(public_hist(r)); seen.add(r['id'])
for x in gem:
    if float(x.get('added_human_score') or 0) < 7 or x['id'] in seen: continue
    rows.append(public_gem(x)); seen.add(x['id'])
data={'schema_version':'2.2','dataset':'gem_mined_human7_unreviewed_v1','dataset_version':'2026-11-21','items':rows}
data['dataset_sha256']=hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
(OUT/'data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('selected',len(rows),'historical',sum(x['batch'].startswith('后续') for x in rows),'gem',sum(x['batch'].startswith('GEM') for x in rows))

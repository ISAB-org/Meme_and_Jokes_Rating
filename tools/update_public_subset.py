import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "transfer_1113_analysis" / "tech-humor-benchmark" / "1119_first100_plus_scored_gem"
items = json.loads((SOURCE / "items.json").read_text())

# Keep the first-round five-category material and retain only the scored extras
# whose human score is at least 7.  The first-round entries have no added score.
keep = [x for x in items if x.get("added_human_score") is None or x.get("added_human_score", 0) >= 7]

out = []
for x in keep:
    domain = x.get("subdomain") or x.get("group") or "未分类"
    out.append({
        "id": x["id"], "original_id": x["id"], "legacy_gem_id": x["id"],
        "domain_id": x.get("group", "other"), "domain_zh": domain,
        "batch": x.get("collection_batch", "原始五类别"),
        "title": x.get("text", "")[:80], "original_text": x.get("text", ""),
        "translation_zh": x.get("text", ""), "translation_status": "原始中文/已随附译文",
        "image_path": (x.get("image_paths") or [None])[0],
        "organizer_context": "", "explanation": x.get("explanation", ""),
        "required_knowledge": "", "content_sha256": hashlib.sha256(x.get("text", "").encode()).hexdigest(),
        "source": {"url": x.get("source_url", ""), "limitation": x.get("source_limitation", "")},
        "points": x.get("points", []),
        "mechanism_tags_suggested": [x.get("mechanism_current", "")],
        "human_score": x.get("added_human_score"),
    })

data = {"schema_version": "2.1", "dataset": "gem_first_round_plus_human7_v1",
        "dataset_version": "2026-11-21", "items": out}
data["dataset_sha256"] = hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
(ROOT / "docs" / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

# Bring over any images referenced by the selected subset.
target = ROOT / "docs" / "images"; target.mkdir(exist_ok=True)
for x in keep:
    for rel in x.get("image_paths") or []:
        src = SOURCE / rel; dst = target / Path(rel).name
        if src.exists() and not dst.exists(): shutil.copy2(src, dst)
print(f"selected={len(out)} original5_categories={sorted({x['domain_id'] for x in out})}")

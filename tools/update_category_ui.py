from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'docs/app.js'
s=p.read_text().replace("data.json?v=20261121-925", "data.json?v=20261121-seven-categories")
s=s.replace("new Map(items.map(x=>[x.domain_id,x.domain_zh]))", "new Map(items.map(x=>[x.domain_id,x.domain_id]))")
s=s.replace("['笑话条目',460]", "['笑话条目',items.length]").replace("['小领域',new Set", "['主类别',new Set")
p.write_text(s)
p=root/'README.md'
s=p.read_text()+'\n当前主类别：铁路、航空、知乎回答、苏联、其他领域、摄影、Anthropic/Claude。摄影与 Anthropic/Claude 已从其他领域中独立，保留原小领域标签。\n'
p.write_text(s)

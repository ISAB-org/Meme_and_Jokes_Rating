from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'docs/index.html'
s = p.read_text()
s = s.replace('460条笑话，中英对照与图片，匿名评分并导出JSON', '158条笑话，中英对照与图片，匿名评分并导出JSON')
s = s.replace('共460条；200条短笑话标注为AI生成；260条候选的来源与审核结论沿用随附资料，待进一步人工核验。', '共158条；当前仅保留铁路、航空、知乎回答、苏联、其他领域五类。')
p.write_text(s)

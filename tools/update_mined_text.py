from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'docs/index.html'; s=p.read_text()
s=s.replace('158条笑话','925条后续挖掘笑话').replace('共158条；当前仅保留铁路、航空、知乎回答、苏联、其他领域五类。','共925条；仅包含 GEM 与其他后续挖掘的高分、未人工复核条目。')
s=s.replace('不要清理此网站的数据；换设备前请导出备份。','本页已移除原一百余条首轮材料。不要清理此网站的数据；换设备前请导出备份。')
p.write_text(s)
p=root/'README.md'; s=p.read_text()
s=s.replace('当前暂保留原始五类（铁路、航空、知乎回答、苏联、其他领域），共158条：首轮材料与首轮之外人工评分≥7的条目。','当前共925条：GEM 与其他后续挖掘中均分≥7、尚未人工复核的条目；原一百余条首轮材料已移除。')
s=s.replace('gem_first_round_plus_human7_v1`，schema_version为2.1','gem_mined_human7_unreviewed_v1`，schema_version为2.2').replace('当前158条的公开内容版本','当前925条的公开内容版本')
p.write_text(s)

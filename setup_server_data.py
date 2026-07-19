#!/usr/bin/env python3
"""Setup server with all needed data."""
import sqlite3, json

db = sqlite3.connect('/opt/kaoyan-assistant/data/kaoyan.db')
db.row_factory = sqlite3.Row
db.execute("DELETE FROM school_info")

schools = [
("厦门大学",2025,"应用统计专硕","政治,英语一,数学三,432统计学",350,42,300,
 json.dumps(["贾俊平《统计学》第7版","茆诗松《概率论与数理统计教程》第3版"]),
 "2025复试线350，统计学系统考录32人(含联培6人)，复录比1.3:1。王亚南研究院录10人，最低366。学制3年。注意:厦大考英语一!","",1),
("厦门大学",2024,"应用统计专硕","政治,英语一,数学三,432统计学",360,25,280,
 json.dumps(["贾俊平《统计学》","茆诗松《概率论》"]),"","",1),
("厦门大学",2023,"应用统计专硕","政治,英语一,数学三,432统计学",364,23,147,
 json.dumps(["贾俊平《统计学》"]),"报录比6.39:1","",1),
("厦门大学",2025,"录取分数(统计系)","最高409最低378中位392",0,0,0,
 json.dumps(["政治均68","英语均68","数学均130","专业课均128","总分均394"]),"建议目标385+","",1),
("西安交通大学",2025,"应用统计专硕","政治,英语二,数学三,432统计学",345,32,320,
 json.dumps(["贾俊平《统计学》第8版","李子奈《计量经济学》第5版","伍德里奇《计量经济学导论》第5版"]),
 "经金学院COT方向。2025复试线345，复试47录32。学制3年。西交考英语二!专业课含计量经济学60分!","",1),
("西安交通大学",2024,"应用统计专硕","政治,英语二,数学三,432统计学",350,29,300,
 json.dumps(["贾俊平《统计学》","李子奈《计量经济学》"]),"录取最低362","",1),
("西安交通大学",2023,"应用统计专硕","政治,英语二,数学三,432统计学",370,27,280,
 json.dumps(["贾俊平《统计学》"]),"复试线370","",1),
("西安交通大学",2025,"录取分数(经金学院)","最高417最低356均分378",0,0,0,
 json.dumps(["政治57-71均64.5","英语二60-85均75.8","数学三101-138均123","432统计94-136均115"]),"建议目标380+","",1),
("考研日程",2026,"2026-2027考研时间线","",0,0,0,
 json.dumps(["9月中旬:各校发布招生简章","9/24-27:预报名","10/8-25:正式报名","11月初:网上确认","12/26-27:初试"]),
 "2027考研完整时间线","",1),
]

for row in schools:
    db.execute("INSERT INTO school_info (school_name,year,major,exam_subjects,admission_line,enrollment_count,applicant_count,reference_books,notes,announcement_text,is_pinned) VALUES (?,?,?,?,?,?,?,?,?,?,?)", row)
db.commit()

# Verify
for t in ['vocab_words','school_info','writing_essays','flashcards']:
    c = db.execute(f"SELECT COUNT(*) as c FROM {t}").fetchone()['c']
    print(f'{t}: {c}')

db.close()
print('Server data setup complete!')

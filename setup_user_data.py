"""Setup user 炊饼 with complete study data."""
import urllib.request, json, sys, functools
print = functools.partial(print, flush=True)

BASE = 'http://localhost:8000'

def api(method, path, token, body=None):
    url = BASE + path
    data = json.dumps(body).encode('utf-8') if body else None
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f'  ERROR {e.code}: {e.read().decode()[:200]}')
        return None

# Login
data = urllib.parse.urlencode({'username': '炊饼', 'password': 'zl6581036'}).encode('utf-8')
req = urllib.request.Request(BASE + '/api/auth/login', data=data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'})
token = json.loads(urllib.request.urlopen(req, timeout=10).read())['access_token']
print('1. Login OK')

# Update settings - 2026 exam
s = api('PUT', '/api/settings', token, {
    'target_school': '厦门大学 + 西安交通大学',
    'exam_date': '2026-12-26',
    'foundation_start': '2025-09-01', 'foundation_end': '2026-03-31',
    'intensive_start': '2026-04-01', 'intensive_end': '2026-08-31',
    'sprint_start': '2026-09-01', 'sprint_end': '2026-12-25',
    'daily_new_words': 50,
    'pomodoro_focus_minutes': 25, 'pomodoro_short_break_minutes': 5,
    'pomodoro_long_break_minutes': 15
})
print(f'2. Settings updated: exam={s["exam_date"]}, countdown starts')

# Get subject IDs
subj_map = {}
subjects = api('GET', '/api/dashboard/overview', token)['subject_progress']
seen = set()
for s in subjects:
    if s['name'] not in seen:
        seen.add(s['name'])
        subj_map[s['name']] = s['subject_id']
print(f'3. Subjects: {subj_map}')

# Create tasks
tasks_data = [
    # Foundation (past)
    ('政治马原全部章节学习', '政治', 'foundation', 2),
    ('英语二5500词汇第一轮背诵', '英语二', 'foundation', 2),
    ('数学三高等数学上下册', '数学三', 'foundation', 2),
    ('432统计学贾俊平《统计学》通读', '432统计学', 'foundation', 2),
    ('政治毛中特全部章节', '政治', 'foundation', 1),
    ('英语二长难句专项训练', '英语二', 'foundation', 1),
    ('数学三线性代数全部章节', '数学三', 'foundation', 1),
    ('英语二真题阅读精读(2010-2016)', '英语二', 'foundation', 1),
    # Intensive (current)
    ('政治史纲+思修法基', '政治', 'intensive', 2),
    ('政治选择题刷题(1000题)', '政治', 'intensive', 2),
    ('英语二真题阅读精读(2017-2022)', '英语二', 'intensive', 2),
    ('英语二翻译专项训练', '英语二', 'intensive', 1),
    ('英语二完形填空专项训练', '英语二', 'intensive', 1),
    ('数学三概率论与数理统计', '数学三', 'intensive', 2),
    ('数学三真题训练(2010-2018)', '数学三', 'intensive', 2),
    ('数学三660题刷题', '数学三', 'intensive', 1),
    ('432统计学茆诗松《概率论与数理统计》', '432统计学', 'intensive', 2),
    ('432统计学真题训练', '432统计学', 'intensive', 2),
    ('432统计学课后习题全刷', '432统计学', 'intensive', 1),
    ('英语二写作模板整理+练习', '英语二', 'intensive', 1),
    # Sprint (future)
    ('政治时政热点整理+背诵', '政治', 'sprint', 2),
    ('政治分析题模板背诵', '政治', 'sprint', 2),
    ('政治模拟卷(肖四肖八)', '政治', 'sprint', 2),
    ('英语二近3年真题全真模拟', '英语二', 'sprint', 2),
    ('英语二作文背诵+默写', '英语二', 'sprint', 2),
    ('数学三真题模拟(2019-2024)', '数学三', 'sprint', 2),
    ('数学三错题回顾+公式速记', '数学三', 'sprint', 1),
    ('432统计学冲刺模拟卷', '432统计学', 'sprint', 2),
    ('432统计学简答题背诵', '432统计学', 'sprint', 2),
    ('全科知识框架最终梳理', '432统计学', 'sprint', 1),
]

all_tasks = []
for title, subj, phase, priority in tasks_data:
    sid = subj_map.get(subj)
    if sid:
        t = api('POST', '/api/tasks', token, {
            'title': title, 'subject_id': sid, 'phase': phase,
            'priority': priority, 'status': 'todo',
            'estimated_minutes': 120 if priority == 2 else 90
        })
        if t: all_tasks.append(t)

print(f'4. Created {len(all_tasks)} tasks')

# Mark foundation tasks done
done = 0
for t in all_tasks:
    for title, subj, phase, pri in tasks_data:
        if phase == 'foundation' and t['title'] == title:
            api('PATCH', f'/api/tasks/{t["id"]}/status', token, {'status': 'done'})
            done += 1
            break
print(f'5. Marked {done} foundation tasks as complete')

# School info
for school, line, enr, app in [
    ('厦门大学', 380, 25, 280),
    ('西安交通大学', 370, 30, 250)
]:
    api('POST', '/api/schools', token, {
        'school_name': school, 'year': 2025, 'major': '应用统计专硕',
        'exam_subjects': '政治,英语二,数学三,432统计学',
        'admission_line': line, 'enrollment_count': enr,
        'applicant_count': app,
        'reference_books': '["贾俊平《统计学》","茆诗松《概率论与数理统计》"]' if school == '厦门大学' else '["袁卫《统计学》","茆诗松《概率论与数理统计》"]',
        'notes': '', 'announcement_text': '', 'is_pinned': 1
    })
print('6. School info added (厦大+西交)')

# Notes
notes = [
    ('政治马原第一章思维导图', 'note', '政治', '# 马克思主义哲学\n\n## 唯物辩证法\n- 联系的观点\n- 发展的观点\n- 矛盾的观点\n\n## 认识论\n- 实践与认识\n- 真理的检验标准', '政治,马原'),
    ('数学三高数公式汇总', 'note', '数学三', '# 高等数学公式\n\n## 导数\n- (x^n)\' = nx^(n-1)\n- (e^x)\' = e^x\n\n## 积分\n- ∫x^n dx = x^(n+1)/(n+1) + C', '数学,公式'),
    ('英语二写作模板-建议信', 'note', '英语二', '# 建议信模板\n\nDear ___, I am writing to express my suggestions regarding ___.\n\nFirst and foremost, ___. Secondly, ___.\n\nI hope you will take my suggestions into consideration.', '英语,写作'),
    ('432统计学-假设检验要点', 'note', '432统计学', '# 假设检验\n\n## 步骤\n1. 提出原假设H0和备择假设H1\n2. 选择检验统计量\n3. 确定显著性水平α\n4. 计算p值\n5. 做出决策', '432统计,核心'),
]
for title, ntype, subj, content, tags in notes:
    sid = subj_map.get(subj)
    if sid:
        api('POST', '/api/notes', token, {
            'type': ntype, 'subject_id': sid, 'title': title,
            'content': content, 'tags': tags
        })
print(f'7. Created {len(notes)} notes')

# Wrong questions
wrongs = [
    ('数学-不定积分计算错误', '数学三', '计算 ∫x/(x²+1) dx，错误使用了分部积分法，正确做法是换元法 u=x²+1'),
    ('政治-混淆唯物辩证法和唯物史观', '政治', '选择题混淆了唯物辩证法和唯物史观，辩证法是关于联系发展的科学，唯物史观是社会存在决定社会意识'),
    ('英语-阅读理解推断题失分', '英语二', '2020年Text3第2题：未能根据上下文推断作者隐含态度，注意转折词but/however后的内容'),
]
for title, subj, content in wrongs:
    sid = subj_map.get(subj)
    if sid:
        api('POST', '/api/notes', token, {
            'type': 'wrong_question', 'subject_id': sid, 'title': title,
            'content': content, 'tags': '错题'
        })
print(f'8. Created {len(wrongs)} wrong questions')

# Flashcards
flashcards = [
    ('政治', '马克思主义最根本的世界观和方法论？', '辩证唯物主义与历史唯物主义', '政治,马原'),
    ('政治', '唯物辩证法的总特征？', '联系的观点和发展的观点', '政治,马原'),
    ('政治', '矛盾的两种基本属性？', '同一性和斗争性', '政治,马原'),
    ('432统计学', '什么是p值？', '在原假设为真时，观察到检验统计量比当前值更极端的概率', '432统计,假设检验'),
    ('432统计学', '第一类错误（α错误）？', '原假设为真时拒绝原假设，即弃真错误', '432统计,假设检验'),
    ('432统计学', '第二类错误（β错误）？', '原假设为假时接受原假设，即取伪错误', '432统计,假设检验'),
    ('数学三', '写出泰勒展开式', "f(x)=f(a)+f'(a)(x-a)+f''(a)/2!(x-a)²+...", '数学,公式'),
    ('数学三', '协方差公式？', 'Cov(X,Y) = E(XY) - E(X)E(Y)', '数学,概率'),
    ('英语二', 'controversy', 'n. 争议；争论', '英语,高频词'),
    ('英语二', 'substantial', 'adj. 大量的；实质的', '英语,高频词'),
]
for subj_name, front, back, tags in flashcards:
    sid = subj_map.get(subj_name)
    if sid:
        api('POST', '/api/flashcards', token, {
            'subject_id': sid, 'front_text': front,
            'back_text': back, 'tags': tags
        })
print(f'9. Created {len(flashcards)} flashcards')

# Reading records
for year, passage, ptype, total, wrong, score in [
    (2020, 'Text 3', 'reading', 5, 1, 4),
    (2020, 'Text 4', 'reading', 5, 2, 3),
    (2019, '翻译', 'translation', 5, 2, 6),
    (2019, '完形填空', 'cloze', 20, 5, 15),
]:
    r = api('POST', '/api/reading', token, {
        'year': year, 'passage_no': passage, 'type': ptype,
        'total_questions': total, 'wrong_count': wrong,
        'score': score, 'time_spent_minutes': 25, 'notes': ''
    })
print(f'10. Created reading records')

# Daily checkins for past week
import datetime
for i in range(7, 0, -1):
    d = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
    api('POST', '/api/checkins', token, {
        'date': d, 'review_text': f'学习记录 {d}',
        'mood': 'good', 'tomorrow_plan': '继续推进'
    })
print('11. Created 7 days of checkins')

# Final state
d = api('GET', '/api/dashboard/overview', token)
print(f'\n{"="*50}')
print(f'FINAL STATE:')
print(f'  Countdown: {d["countdown_days"]} days until exam')
print(f'  Streak: {d["streak_days"]} days')
print(f'  Today mins: {d["today_minutes"]}')
print(f'  Tasks: {d["today_tasks_count"]} today')
print(f'  Subjects: {len(d["subject_progress"])}')
completed = sum(1 for t in all_tasks if any(ft[0] == t['title'] for ft in tasks_data if ft[2] == 'foundation'))
print(f'  Total tasks: {len(all_tasks)} ({done} done)')
print(f'{"="*50}')
print('Setup complete!')

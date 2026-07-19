import sqlite3, datetime

db = sqlite3.connect('data/kaoyan.db')
db.row_factory = sqlite3.Row

# Add vocab
words = [
    ('acquire', '/əˈkwaɪər/', 'v.', '获得；习得', 'Students acquire knowledge through reading and practice.', '学生通过阅读和练习获得知识。', 'high'),
    ('adequate', '/ˈædɪkwət/', 'adj.', '充足的；适当的', 'The library provides adequate resources.', '图书馆提供了充足的资源。', 'high'),
    ('advocate', '/ˈædvəkeɪt/', 'v.', '提倡；主张', 'Many educators advocate for smaller class sizes.', '许多教育工作者主张缩小班级规模。', 'high'),
    ('alternative', '/ɔːlˈtɜːrnətɪv/', 'n.', '替代方案', 'We need to find an alternative to fossil fuels.', '我们需要找到替代方案。', 'high'),
    ('ambiguous', '/æmˈbɪɡjuəs/', 'adj.', '模棱两可的', 'The statement was deliberately ambiguous.', '声明故意含糊其辞。', 'high'),
    ('analyze', '/ˈænəlaɪz/', 'v.', '分析', 'Researchers analyze data to find patterns.', '研究人员分析数据以发现模式。', 'high'),
    ('anticipate', '/ænˈtɪsɪpeɪt/', 'v.', '预期；预料', 'We anticipate a rise in demand.', '我们预计需求会上升。', 'high'),
    ('appreciate', '/əˈpriːʃieɪt/', 'v.', '欣赏；感激', 'I appreciate your help with this project.', '感谢你对这个项目的帮助。', 'high'),
    ('appropriate', '/əˈproʊpriət/', 'adj.', '适当的', 'Please take appropriate measures.', '请采取适当措施。', 'high'),
    ('assume', '/əˈsuːm/', 'v.', '假设；承担', 'We cannot assume the results will be consistent.', '不能假设结果会一致。', 'high'),
    ('capable', '/ˈkeɪpəbl/', 'adj.', '有能力的', 'She is capable of handling complex tasks.', '她能处理复杂任务。', 'high'),
    ('challenge', '/ˈtʃælɪndʒ/', 'n./v.', '挑战', 'Climate change is the biggest challenge we face.', '气候变化是最大挑战。', 'high'),
    ('circumstance', '/ˈsɜːrkəmstæns/', 'n.', '环境；情况', 'Under no circumstances should you give up.', '不要放弃。', 'high'),
    ('compensate', '/ˈkɒmpenseɪt/', 'v.', '补偿；赔偿', 'The company will compensate workers.', '公司将补偿工人。', 'high'),
    ('component', '/kəmˈpoʊnənt/', 'n.', '组成部分', 'Trust is a key component of any relationship.', '信任是关系的关键组成部分。', 'high'),
    ('concentrate', '/ˈkɒnsntreɪt/', 'v.', '集中；专注', 'I need to concentrate on my studies.', '我需要专注学习。', 'high'),
    ('concept', '/ˈkɒnsept/', 'n.', '概念；观念', 'The concept of justice varies across cultures.', '正义概念因文化而异。', 'high'),
    ('conclude', '/kənˈkluːd/', 'v.', '得出结论', 'The study concluded that diet affects longevity.', '研究结论是饮食影响寿命。', 'high'),
    ('conduct', '/kənˈdʌkt/', 'v.', '进行；实施', 'The team will conduct a survey.', '团队将进行调查。', 'high'),
    ('consequence', '/ˈkɒnsɪkwəns/', 'n.', '结果；后果', 'The consequences could be severe.', '后果可能很严重。', 'high'),
    ('considerable', '/kənˈsɪdərəbl/', 'adj.', '相当大的', 'A considerable amount of research supports this.', '大量研究支持这一点。', 'high'),
    ('consistent', '/kənˈsɪstənt/', 'adj.', '一致的', 'Her performance has been consistently excellent.', '她表现一贯优秀。', 'high'),
    ('contribute', '/kənˈtrɪbjuːt/', 'v.', '贡献；捐助', 'Everyone can contribute to protecting the environment.', '人人能为环保出力。', 'high'),
    ('controversy', '/ˈkɒntrəvɜːrsi/', 'n.', '争议；争论', 'The proposal has caused controversy.', '提议引起了争议。', 'high'),
    ('convince', '/kənˈvɪns/', 'v.', '说服；使信服', 'He convinced the committee.', '他说服了委员会。', 'high'),
    ('crisis', '/ˈkraɪsɪs/', 'n.', '危机', 'The financial crisis affected millions.', '金融危机影响了几百万人。', 'high'),
    ('crucial', '/ˈkruːʃl/', 'adj.', '关键的', 'This decision is crucial for the future.', '这个决定至关重要。', 'high'),
    ('demonstrate', '/ˈdemənstreɪt/', 'v.', '证明；展示', 'The experiment demonstrates the effectiveness.', '实验证明了有效性。', 'high'),
    ('despite', '/dɪˈspaɪt/', 'prep.', '尽管', 'Despite the difficulties, she completed the project.', '尽管有困难，她完成了。', 'high'),
    ('determine', '/dɪˈtɜːrmɪn/', 'v.', '决定；确定', 'Further research is needed to determine the cause.', '需要更多研究来确定原因。', 'high'),
    ('distinguish', '/dɪˈstɪŋɡwɪʃ/', 'v.', '区分；辨别', 'Distinguish between fact and opinion.', '区分事实和观点。', 'high'),
    ('domestic', '/dəˈmestɪk/', 'adj.', '国内的；家庭的', 'Domestic consumption has increased.', '国内消费增加了。', 'high'),
    ('dramatic', '/drəˈmætɪk/', 'adj.', '戏剧性的；巨大的', 'There has been a dramatic increase.', '出现了大幅增长。', 'high'),
    ('eliminate', '/ɪˈlɪmɪneɪt/', 'v.', '消除；淘汰', 'We must eliminate all sources of error.', '必须消除所有误差。', 'high'),
    ('emerge', '/ɪˈmɜːrdʒ/', 'v.', '出现；浮现', 'New evidence has emerged.', '出现了新证据。', 'high'),
    ('emphasis', '/ˈemfəsɪs/', 'n.', '强调；重点', 'Great emphasis is placed on education.', '高度重视教育。', 'high'),
    ('enable', '/ɪˈneɪbl/', 'v.', '使能够', 'Technology enables us to communicate globally.', '技术使我们能全球沟通。', 'high'),
    ('enhance', '/ɪnˈhæns/', 'v.', '提高；增强', 'Exercise can enhance health.', '运动能增强健康。', 'high'),
    ('enormous', '/ɪˈnɔːrməs/', 'adj.', '巨大的', 'The project required enormous work.', '项目需要大量工作。', 'high'),
    ('ensure', '/ɪnˈʃʊr/', 'v.', '确保', 'Please ensure all doors are locked.', '请确保所有门都锁好。', 'high'),
    ('establish', '/ɪˈstæblɪʃ/', 'v.', '建立；确立', 'The company was established in 1995.', '公司成立于1995年。', 'high'),
    ('evaluate', '/ɪˈvæljueɪt/', 'v.', '评估；评价', 'We need to evaluate the new policy.', '需要评估新政策。', 'high'),
    ('evidence', '/ˈevɪdəns/', 'n.', '证据；证明', 'There is strong evidence for this.', '有强有力的证据。', 'high'),
    ('exceed', '/ɪkˈsiːd/', 'v.', '超过；超越', 'The results exceeded expectations.', '结果超预期。', 'high'),
    ('exploit', '/ɪkˈsplɔɪt/', 'v.', '利用；开发', 'Do not exploit workers.', '不要剥削工人。', 'high'),
    ('external', '/ɪkˈstɜːrnl/', 'adj.', '外部的', 'External factors play a role.', '外部因素有影响。', 'high'),
    ('facilitate', '/fəˈsɪlɪteɪt/', 'v.', '促进；便利', 'Software facilitates the process.', '软件促进了流程。', 'high'),
    ('fundamental', '/ˌfʌndəˈmentl/', 'adj.', '基本的', 'This is a fundamental principle.', '这是基本原则。', 'high'),
    ('generate', '/ˈdʒenəreɪt/', 'v.', '产生；生成', 'The project will generate revenue.', '项目会产生收入。', 'high'),
    ('guarantee', '/ˌɡærənˈtiː/', 'v./n.', '保证', 'Hard work does not guarantee success.', '努力不保证成功。', 'high'),
]

added = 0
for w in words:
    exist = db.execute('SELECT id FROM vocab_words WHERE word=?', (w[0],)).fetchone()
    if exist: continue
    db.execute('INSERT INTO vocab_words (word,phonetic,part_of_speech,meaning,example_sentence,example_translation,frequency_level,is_custom,status) VALUES (?,?,?,?,?,?,?,0,"new")', w)
    added += 1
db.commit()
print(f'Words: +{added}, total={db.execute("SELECT COUNT(*) FROM vocab_words").fetchone()[0]}')

# Reading records
readings = [
    (2023, 'Text 1', 'reading', 5, 1, 4, '塑料污染与环保创新'),
    (2023, 'Text 2', 'reading', 5, 1, 4, '美国劳动力市场变化'),
    (2023, 'Text 3', 'reading', 5, 2, 3, '社交媒体对青少年的影响'),
    (2023, 'Text 4', 'reading', 5, 1, 4, '科学研究方法的演变'),
    (2023, '翻译', 'translation', 5, 1, 8, '文学翻译'),
    (2023, '完形填空', 'cloze', 20, 4, 16, '教育与经济发展'),
    (2022, 'Text 1', 'reading', 5, 1, 4, '气候变化对农业的影响'),
    (2022, 'Text 2', 'reading', 5, 2, 3, '美国退休储蓄危机'),
    (2022, 'Text 3', 'reading', 5, 1, 4, '人工智能与就业'),
    (2022, 'Text 4', 'reading', 5, 1, 4, '道德心理学研究'),
    (2022, '翻译', 'translation', 5, 2, 7, '社科类翻译'),
    (2022, '完形填空', 'cloze', 20, 5, 15, '语言学习与认知'),
    (2021, 'Text 1', 'reading', 5, 2, 3, '英国食品安全'),
    (2021, 'Text 2', 'reading', 5, 1, 4, '可再生能源发展'),
    (2021, 'Text 3', 'reading', 5, 1, 4, '远程工作的利弊'),
    (2021, 'Text 4', 'reading', 5, 2, 3, '行为经济学研究'),
    (2021, '翻译', 'translation', 5, 1, 8, '社科类翻译'),
    (2021, '完形填空', 'cloze', 20, 4, 16, '技术进步与社会变迁'),
    (2020, 'Text 1', 'reading', 5, 1, 4, '机器人与就业市场'),
    (2020, 'Text 2', 'reading', 5, 2, 3, 'CEO薪酬问题'),
    (2020, 'Text 3', 'reading', 5, 1, 4, '科技伦理'),
    (2020, 'Text 4', 'reading', 5, 1, 4, '经济政策分析'),
    (2020, '翻译', 'translation', 5, 2, 7, '文学类翻译'),
    (2020, '完形填空', 'cloze', 20, 5, 15, '亲子关系研究'),
    (2019, 'Text 1', 'reading', 5, 1, 4, '情绪与决策'),
    (2019, 'Text 2', 'reading', 5, 1, 4, '森林碳汇'),
    (2019, 'Text 3', 'reading', 5, 2, 3, '美国移民问题'),
    (2019, 'Text 4', 'reading', 5, 1, 4, '抗生素耐药性'),
    (2019, '翻译', 'translation', 5, 1, 7, '人物传记翻译'),
    (2019, '完形填空', 'cloze', 20, 4, 16, '手机使用与健康'),
]

now = datetime.datetime.now().isoformat()
for r in readings:
    db.execute('INSERT INTO reading_records (year,passage_no,type,total_questions,wrong_count,score,time_spent_minutes,notes,created_at) VALUES (?,?,?,?,?,?,?,?,?)',
               (r[0], r[1], r[2], r[3], r[4], r[5], 20, f'题材：{r[6]}', now))
db.commit()
print(f'Reading: {db.execute("SELECT COUNT(*) FROM reading_records").fetchone()[0]} records')

# Writing templates
templates = [
    ('small', '建议信模板',
     'Dear Sir or Madam,\n\nI am writing to express my suggestions regarding [topic].\n\n'
     'First and foremost, I would like to propose that [suggestion 1]. This would greatly benefit [target] because [reason].\n\n'
     'Secondly, it would be highly appreciated if [suggestion 2] could be taken into consideration.\n\n'
     'Thank you for taking the time to consider my suggestions. I look forward to seeing positive changes.\n\n'
     'Yours sincerely,\nLi Ming'),
    ('small', '投诉信模板',
     'Dear Sir or Madam,\n\nI am writing to express my dissatisfaction with [product/service] which I purchased from your store on [date].\n\n'
     'Unfortunately, I found that [specific problem]. This is very disappointing because [reason].\n\n'
     'I would appreciate it if you could [expected solution], or I would like to request [compensation].\n\n'
     'I look forward to your prompt reply.\n\nYours sincerely,\nLi Ming'),
    ('small', '邀请信模板',
     'Dear [Name],\n\nI am writing to invite you to [event] which will be held on [date] at [place].\n\n'
     'The event will begin at [time] and will include [activities]. I believe you will find it [benefit].\n\n'
     'Please let me know if you can attend by [RSVP date]. I sincerely hope you can join us.\n\n'
     'Yours sincerely,\nLi Ming'),
    ('small', '感谢信模板',
     'Dear [Name],\n\nI am writing to express my heartfelt gratitude for [what they did].\n\n'
     'Your help made a significant difference because [reason]. Without your help, I would not have been able to [achievement].\n\n'
     'I truly appreciate everything you have done.\n\nYours sincerely,\nLi Ming'),
    ('small', '道歉信模板',
     'Dear [Name],\n\nI am writing to sincerely apologize for [what happened].\n\n'
     'I fully understand that my action caused you inconvenience, and I take full responsibility for it.\n\n'
     'To make up for this, I would like to [remedy]. I promise that such a situation will not happen again.\n\n'
     'Yours sincerely,\nLi Ming'),
    ('small', '求职信模板',
     'Dear Sir or Madam,\n\nI am writing to apply for the position of [job title] as advertised on [source].\n\n'
     'I am currently a [major] major at [university]. During my studies, I have developed strong skills in [skill 1] and [skill 2].\n\n'
     'I believe my qualifications make me a strong candidate for this position. I have attached my resume for your review.\n\n'
     'Thank you for your consideration. I look forward to hearing from you.\n\nYours sincerely,\nLi Ming'),
    ('large', '图表作文-柱状图模板',
     'As is clearly shown in the bar chart, [describe the data trend]. Specifically, [key data point 1] increased/decreased from [A] to [B] during the period, while [key data point 2] rose/fell from [C] to [D].\n\n'
     'Several factors may contribute to this phenomenon. First and foremost, [reason 1]. Secondly, [reason 2] has played a significant role.\n\n'
     'From my perspective, this trend is likely to continue in the foreseeable future. Therefore, [suggestion].'),
    ('large', '图表作文-折线图模板',
     'The line graph illustrates the changes in [topic] over the period from [start year] to [end year]. '
     'As can be seen, the number of [item] experienced a [steady/dramatic] [increase/decrease], from [A] to [B].\n\n'
     'There are several reasons behind this trend. To begin with, [reason 1]. In addition, [reason 2] has also contributed.\n\n'
     'Based on the analysis, we can conclude that [conclusion]. In the coming years, [prediction].'),
    ('large', '图表作文-饼图模板',
     'The pie chart presents the proportion of [categories] in [context]. It is noticeable that [largest category] accounts for the largest share at [X]%, followed by [second category] at [Y]%.\n\n'
     'The data reflects several important trends. Primarily, [analysis of largest segment]. Furthermore, [analysis of another segment].\n\n'
     'In conclusion, the pie chart reveals that [main finding].'),
    ('large', '议论文-观点论证模板',
     'When it comes to [topic], opinions vary from person to person. Some believe that [view A], while others argue that [view B]. From my perspective, I support the former/latter view.\n\n'
     'First and foremost, [argument 1]. For instance, [example]. Secondly, [argument 2]. Research has shown that [evidence].\n\n'
     'Admittedly, [counterargument] has some merit. However, [refutation].\n\n'
     'In conclusion, I firmly believe that [restate position]. It is high time that [call to action].'),
    ('large', '议论文-原因分析模板',
     'In recent years, there has been a growing concern over [phenomenon]. This issue has attracted widespread attention.\n\n'
     'Several factors account for this phenomenon. First, [reason 1]. Secondly, [reason 2] is also responsible. Last but not least, [reason 3].\n\n'
     'To address this issue, I suggest that [solution 1] and [solution 2]. Only through joint efforts can we [positive outcome].'),
    ('large', '议论文-利弊分析模板',
     'The issue of [topic] has been brought to public attention recently. Like a double-edged sword, it brings both advantages and disadvantages.\n\n'
     'On the one hand, [advantage 1] and [advantage 2] can greatly benefit [aspect]. On the other hand, [disadvantage 1] may lead to [negative consequence].\n\n'
     'In conclusion, the merits outweigh the demerits. With proper guidance, we can maximize benefits while minimizing negative impacts.'),
    ('small', '练习-图书馆建议信',
     'Dear Librarian,\n\nI am writing to express my sincere suggestions regarding our university library.\n\n'
     'First and foremost, I would like to propose that the library extend its opening hours during the exam period, as many students find it challenging to secure a seat during peak hours.\n\n'
     'Secondly, it would be highly appreciated if the library could subscribe to more academic journals in the field of statistics.\n\n'
     'Thank you for taking my suggestions into consideration.\n\nSincerely, Li Ming'),
]

for t in templates:
    db.execute('INSERT INTO writing_essays (type,title,content,created_at) VALUES (?,?,?,?)',
               (t[0], t[1], t[2], now))
db.commit()
print(f'Writing: {db.execute("SELECT COUNT(*) FROM writing_essays").fetchone()[0]} templates')

db.close()
print('Done!')

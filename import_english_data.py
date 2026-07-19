"""Import English vocabulary, reading records, and writing templates."""
import httpx, json, sys

r = httpx.post('http://localhost:8000/api/auth/login',
    data={'username': '炊饼', 'password': 'zl6581036'}, timeout=10)
token = r.json()['access_token']
h = {'Authorization': f'Bearer {token}'}

def api(method, path, body=None):
    try:
        url = f'http://localhost:8000{path}'
        resp = httpx.request(method, url, json=body, headers=h, timeout=10)
        return resp.json() if resp.text else None
    except Exception as e:
        print(f'  FAIL {method} {path}: {e}')
        return None

# Check current state
vocab = api('GET', '/api/vocab?limit=1')
reading = api('GET', '/api/reading') or []
writing = api('GET', '/api/writing') or []
print(f'Before: {vocab["total"]} words, {len(reading)} reading, {len(writing)} writing')

# 1. VOCABULARY - additional words
extra_words = [
    ("acquire", "/əˈkwaɪər/", "v.", "获得；习得", "Students acquire knowledge through reading and practice.", "学生通过阅读和练习获得知识。", "high"),
    ("adequate", "/ˈædɪkwət/", "adj.", "充足的；适当的", "The library provides adequate resources for research.", "图书馆为研究提供了充足的资源。", "high"),
    ("advocate", "/ˈædvəkeɪt/", "v.", "提倡；主张", "Many educators advocate for smaller class sizes.", "许多教育工作者主张缩小班级规模。", "high"),
    ("alternative", "/ɔːlˈtɜːrnətɪv/", "n.", "替代方案", "We need to find an alternative to fossil fuels.", "我们需要找到化石燃料的替代方案。", "high"),
    ("ambiguous", "/æmˈbɪɡjuəs/", "adj.", "模棱两可的", "The statement was deliberately ambiguous.", "这个声明故意含糊其辞。", "high"),
    ("analyze", "/ˈænəlaɪz/", "v.", "分析", "Researchers analyze data to find patterns.", "研究人员分析数据以发现模式。", "high"),
    ("anticipate", "/ænˈtɪsɪpeɪt/", "v.", "预期；预料", "We anticipate a rise in demand next quarter.", "我们预计下个季度需求会上升。", "high"),
    ("appreciate", "/əˈpriːʃieɪt/", "v.", "欣赏；感激", "I appreciate your help with this project.", "我感谢你对这个项目的帮助。", "high"),
    ("appropriate", "/əˈproʊpriət/", "adj.", "适当的", "Please take appropriate measures to solve this issue.", "请采取适当措施解决此问题。", "high"),
    ("assume", "/əˈsuːm/", "v.", "假设；承担", "We cannot assume that the results will be consistent.", "我们不能假设结果会是一致的。", "high"),
    ("capable", "/ˈkeɪpəbl/", "adj.", "有能力的", "She is capable of handling complex tasks.", "她有能力处理复杂的任务。", "high"),
    ("challenge", "/ˈtʃælɪndʒ/", "n./v.", "挑战", "Climate change is the biggest challenge we face.", "气候变化是我们面临的最大挑战。", "high"),
    ("circumstance", "/ˈsɜːrkəmstæns/", "n.", "环境；情况", "Under no circumstances should you give up.", "在任何情况下你都不应该放弃。", "high"),
    ("compensate", "/ˈkɒmpenseɪt/", "v.", "补偿；赔偿", "The company will compensate workers for overtime.", "公司将补偿工人的加班时间。", "high"),
    ("component", "/kəmˈpoʊnənt/", "n.", "组成部分；成分", "Trust is a key component of any relationship.", "信任是任何关系的关键组成部分。", "high"),
    ("concentrate", "/ˈkɒnsntreɪt/", "v.", "集中；专注", "I need to concentrate on my studies.", "我需要专注于我的学习。", "high"),
    ("concept", "/ˈkɒnsept/", "n.", "概念；观念", "The concept of justice varies across cultures.", "正义的概念因文化而异。", "high"),
    ("conclude", "/kənˈkluːd/", "v.", "得出结论；结束", "The study concluded that diet affects longevity.", "这项研究得出结论，饮食影响寿命。", "high"),
    ("conduct", "/kənˈdʌkt/", "v.", "进行；实施", "The team will conduct a survey of customer satisfaction.", "团队将进行一次客户满意度调查。", "high"),
    ("consequence", "/ˈkɒnsɪkwəns/", "n.", "结果；后果", "The consequences of inaction could be severe.", "不作为的后果可能很严重。", "high"),
    ("considerable", "/kənˈsɪdərəbl/", "adj.", "相当大的", "A considerable amount of research supports this theory.", "大量研究支持这一理论。", "high"),
    ("consistent", "/kənˈsɪstənt/", "adj.", "一致的；始终如一的", "Her performance has been consistently excellent.", "她的表现一直很优秀。", "high"),
    ("contribute", "/kənˈtrɪbjuːt/", "v.", "贡献；捐助", "Everyone can contribute to protecting the environment.", "每个人都可以为保护环境做出贡献。", "high"),
    ("controversy", "/ˈkɒntrəvɜːrsi/", "n.", "争议；争论", "The proposal has caused considerable controversy.", "这个提议引起了相当大的争议。", "high"),
    ("convince", "/kənˈvɪns/", "v.", "说服；使信服", "He convinced the committee to approve the project.", "他说服委员会批准了这个项目。", "high"),
    ("crisis", "/ˈkraɪsɪs/", "n.", "危机", "The financial crisis affected millions of people.", "金融危机影响了数百万人。", "high"),
    ("crucial", "/ˈkruːʃl/", "adj.", "关键的；决定性的", "This decision is crucial for the future of the company.", "这个决定对公司的未来至关重要。", "high"),
    ("demonstrate", "/ˈdemənstreɪt/", "v.", "证明；展示", "The experiment demonstrates the effectiveness of the drug.", "实验证明了该药物的有效性。", "high"),
    ("despite", "/dɪˈspaɪt/", "prep.", "尽管", "Despite the difficulties, she completed the project on time.", "尽管困难重重，她仍按时完成了项目。", "high"),
    ("determine", "/dɪˈtɜːrmɪn/", "v.", "决定；确定", "Further research is needed to determine the cause.", "需要进一步研究来确定原因。", "high"),
    ("distinguish", "/dɪˈstɪŋɡwɪʃ/", "v.", "区分；辨别", "It is important to distinguish between fact and opinion.", "区分事实和观点很重要。", "high"),
    ("domestic", "/dəˈmestɪk/", "adj.", "国内的；家庭的", "Domestic consumption has increased significantly.", "国内消费显著增长。", "high"),
    ("dramatic", "/drəˈmætɪk/", "adj.", "戏剧性的；巨大的", "There has been a dramatic increase in housing prices.", "房价出现了戏剧性的上涨。", "high"),
    ("eliminate", "/ɪˈlɪmɪneɪt/", "v.", "消除；淘汰", "We must eliminate all sources of error from the experiment.", "我们必须消除实验中的所有误差来源。", "high"),
    ("emerge", "/ɪˈmɜːrdʒ/", "v.", "出现；浮现", "New evidence has emerged that challenges the theory.", "出现了新的证据挑战这一理论。", "high"),
    ("emphasis", "/ˈemfəsɪs/", "n.", "强调；重点", "The government places great emphasis on education.", "政府高度重视教育。", "high"),
    ("enable", "/ɪˈneɪbl/", "v.", "使能够", "Technology enables us to communicate instantly across the globe.", "技术使我们能够在全球范围内即时沟通。", "high"),
    ("enhance", "/ɪnˈhæns/", "v.", "提高；增强", "Exercise can enhance both physical and mental health.", "运动可以增强身心健康。", "high"),
    ("enormous", "/ɪˈnɔːrməs/", "adj.", "巨大的；庞大的", "The project required an enormous amount of work.", "这个项目需要大量的工作。", "high"),
    ("ensure", "/ɪnˈʃʊr/", "v.", "确保", "Please ensure that all doors are locked before leaving.", "请确保离开前所有门都已锁好。", "high"),
    ("establish", "/ɪˈstæblɪʃ/", "v.", "建立；确立", "The company was established in 1995.", "该公司成立于1995年。", "high"),
    ("evaluate", "/ɪˈvæljueɪt/", "v.", "评估；评价", "We need to evaluate the effectiveness of the new policy.", "我们需要评估新政策的有效性。", "high"),
    ("evidence", "/ˈevɪdəns/", "n.", "证据；证明", "There is strong evidence linking smoking to lung cancer.", "有强有力的证据表明吸烟与肺癌有关。", "high"),
    ("exceed", "/ɪkˈsiːd/", "v.", "超过；超越", "The results exceeded our expectations.", "结果超出了我们的预期。", "high"),
    ("exploit", "/ɪkˈsplɔɪt/", "v.", "利用；开发", "Companies should not exploit their workers.", "公司不应该剥削工人。", "high"),
    ("external", "/ɪkˈstɜːrnl/", "adj.", "外部的", "External factors also play a role in economic growth.", "外部因素也在经济增长中发挥作用。", "high"),
    ("facilitate", "/fəˈsɪlɪteɪt/", "v.", "促进；便利", "The new software facilitates the data analysis process.", "新软件促进了数据分析过程。", "high"),
    ("fundamental", "/ˌfʌndəˈmentl/", "adj.", "基本的；根本的", "This is a fundamental principle of economics.", "这是经济学的基本原理。", "high"),
    ("generate", "/ˈdʒenəreɪt/", "v.", "产生；生成", "The project is expected to generate significant revenue.", "该项目预计将产生可观的收入。", "high"),
]

print(f'Adding {len(extra_words)} words...')
added = 0
for word, phonetic, pos, meaning, example, example_trans, freq in extra_words:
    exist = api('GET', f'/api/vocab?search={word}&limit=1')
    if exist and exist.get('total', 0) > 0:
        continue
    api('POST', '/api/vocab/custom', {
        'word': word, 'phonetic': phonetic, 'part_of_speech': pos,
        'meaning': meaning, 'example_sentence': example,
        'example_translation': example_trans, 'frequency_level': freq
    })
    added += 1
print(f'Added {added} new words')

# 2. READING RECORDS
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

print(f'Adding {len(readings)} reading records...')
for year, passage, rtype, total, wrong, score, topic in readings:
    api('POST', '/api/reading', {
        'year': year, 'passage_no': passage, 'type': rtype,
        'total_questions': total, 'wrong_count': wrong,
        'score': score, 'time_spent_minutes': 20, 'notes': f'题材：{topic}'
    })
print('Reading records added')

# 3. WRITING TEMPLATES
templates = [
    ('small', '建议信模板',
     'Dear Sir or Madam,\n\nI am writing to express my suggestions regarding [topic].\n\n'
     'First and foremost, I would like to propose that [suggestion 1]. This would greatly benefit [target] because [reason].\n\n'
     'Secondly, it would be highly appreciated if [suggestion 2] could be taken into consideration.\n\n'
     'Thank you for taking the time to consider my suggestions.\n\nYours sincerely,\nLi Ming'),
    ('small', '投诉信模板',
     'Dear Sir or Madam,\n\nI am writing to express my dissatisfaction with [product/service] which I purchased on [date].\n\n'
     'Unfortunately, I found that [specific problem]. This is very disappointing because [reason].\n\n'
     'I would appreciate it if you could [expected solution], or I would like to request [compensation].\n\n'
     'I look forward to your prompt reply.\n\nYours sincerely,\nLi Ming'),
    ('small', '邀请信模板',
     'Dear [Name],\n\nI am writing to invite you to [event] which will be held on [date] at [place].\n\n'
     'The event will begin at [time] and will include [activities]. I believe you will find it [benefit].\n\n'
     'Please let me know if you can attend by [RSVP date]. I sincerely hope you can join us.\n\nYours sincerely,\nLi Ming'),
    ('small', '感谢信模板',
     'Dear [Name],\n\nI am writing to express my heartfelt gratitude for [what they did].\n\n'
     'Your help made a significant difference because [reason]. Without your help, I would not have been able to [achievement].\n\n'
     'I truly appreciate everything you have done.\n\nYours sincerely,\nLi Ming'),
    ('small', '道歉信模板',
     'Dear [Name],\n\nI am writing to sincerely apologize for [what happened].\n\n'
     'I fully understand that my action caused you inconvenience, and I take full responsibility for it.\n\n'
     'To make up for this, I would like to [remedy]. I promise that such a situation will not happen again.\n\nYours sincerely,\nLi Ming'),
    ('small', '求职信模板',
     'Dear Sir or Madam,\n\nI am writing to apply for the position of [job title] as advertised on [source].\n\n'
     'I am currently a [major] major at [university]. During my studies, I have developed strong skills in [skill 1] and [skill 2].\n\n'
     'I believe my qualifications make me a strong candidate. I have attached my resume for your review.\n\n'
     'Thank you for your consideration.\n\nYours sincerely,\nLi Ming'),
    ('large', '图表作文模板-柱状图',
     'As is clearly shown in the bar chart, [describe the data trend]. Specifically, [key data point 1] increased/decreased from [A] to [B], while [key data point 2] rose/fell from [C] to [D].\n\n'
     'Several factors may contribute to this phenomenon. First and foremost, [reason 1]. Secondly, [reason 2] has played a significant role.\n\n'
     'From my perspective, this trend is likely to continue. Only by taking appropriate measures can we [achieve positive outcome].'),
    ('large', '图表作文模板-折线图',
     'The line graph illustrates the changes in [topic] over the period from [start year] to [end year]. '
     'As can be seen, the number of [item] experienced a [steady/dramatic] [increase/decrease], from [A] to [B].\n\n'
     'There are several reasons behind this trend. To begin with, [reason 1]. In addition, [reason 2] has also contributed.\n\n'
     'Based on the analysis, we can conclude that [conclusion]. In the coming years, [prediction].'),
    ('large', '图表作文模板-饼图',
     'The pie chart presents the proportion of [categories] in [context]. It is noticeable that [largest category] accounts for the largest share at [X]%, followed by [second category] at [Y]%.\n\n'
     'The data reflects several important trends. Primarily, [analysis of largest segment]. Furthermore, [analysis of another segment].\n\n'
     'In conclusion, the pie chart reveals that [main finding]. This pattern may [continue/change] as [future development].'),
    ('large', '议论文模板-观点论证',
     'When it comes to [topic], opinions vary from person to person. Some believe that [view A], while others argue that [view B]. From my perspective, I support the former/latter view.\n\n'
     'First and foremost, [argument 1]. For instance, [example]. Secondly, [argument 2]. Research has shown that [evidence].\n\n'
     'Admittedly, [counterargument] has some merit. However, [refutation].\n\n'
     'In conclusion, I firmly believe that [restate position]. It is high time that [call to action].'),
    ('large', '议论文模板-原因分析',
     'In recent years, there has been a growing concern over [phenomenon]. This issue has attracted widespread attention.\n\n'
     'Several factors account for this phenomenon. First, [reason 1]. Secondly, [reason 2] is also responsible. Last but not least, [reason 3].\n\n'
     'To address this issue, I suggest that [solution 1] and [solution 2]. Only through joint efforts can we [positive outcome].'),
    ('large', '议论文模板-利弊分析',
     'The issue of [topic] has been brought to public attention recently. Like a double-edged sword, it brings both advantages and disadvantages.\n\n'
     'On the one hand, [advantage 1] and [advantage 2] can greatly benefit [aspect]. On the other hand, [disadvantage 1] may lead to [negative consequence].\n\n'
     'In conclusion, the merits outweigh the demerits. With proper guidance, we can maximize benefits while minimizing negative impacts.'),
    ('small', '练习：图书馆建议信',
     'Dear Librarian,\n\nI am writing to express my suggestions regarding our university library.\n\n'
     'First, I would like to propose that the library extend its opening hours during the exam period. Many students find it challenging to secure a seat.\n\n'
     'Secondly, it would be appreciated if the library could subscribe to more academic journals in statistics.\n\n'
     'Thank you for taking my suggestions into consideration.\n\nSincerely, Li Ming'),
]

print(f'Adding {len(templates)} writing templates...')
for etype, title, content in templates:
    api('POST', '/api/writing', {'type': etype, 'title': title, 'content': content})
print('Writing templates added')

# Final stats
vocab = api('GET', '/api/vocab?limit=1')
reading = api('GET', '/api/reading') or []
writing = api('GET', '/api/writing') or []
print(f'\n=== FINAL ===')
print(f'Words: {vocab["total"]}')
print(f'Reading records: {len(reading)}')
print(f'Writing essays/templates: {len(writing)}')
print('Done!')

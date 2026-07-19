import sqlite3, datetime

db = sqlite3.connect('data/kaoyan.db')
db.row_factory = sqlite3.Row

# Add is_template column
try: db.execute('ALTER TABLE writing_essays ADD COLUMN is_template INTEGER DEFAULT 0')
except: pass

# Clear old essays
db.execute('DELETE FROM writing_essays')
now = datetime.datetime.now().isoformat()

templates = [
    # ===== SMALL ESSAYS (小作文) =====
    # 建议信 x3
    ('small', '【建议信】图书馆改进', 1,
     'Dear Librarian,\n\nI am writing to express my suggestions regarding our university library.\n\n'
     'First and foremost, I would like to propose that the library extend its opening hours during the exam period, as many students find it challenging to secure a seat during peak hours.\n\n'
     'Secondly, it would be highly appreciated if the library could subscribe to more academic journals in the field of statistics, as the current collection is limited.\n\n'
     'Thank you for taking my suggestions into consideration.\n\nYours sincerely,\nLi Ming'),
    ('small', '【建议信】食堂改善', 1,
     'Dear Sir or Madam,\n\nI am writing to offer some suggestions concerning the school canteen.\n\n'
     'To begin with, I suggest that the canteen diversify its menu by adding more vegetable dishes, as a balanced diet is essential for students health.\n\n'
     'Moreover, it would be better if the canteen could extend its service hours, especially during the evening, so that students who study late can have access to warm meals.\n\n'
     'I hope you will find these suggestions helpful.\n\nYours sincerely,\nLi Ming'),
    ('small', '【建议信】课程改进', 1,
     'Dear Professor,\n\nI am writing to share my thoughts on the current course arrangement.\n\n'
     'Firstly, I wonder if it would be possible to provide more practical exercises in class, as hands-on practice can deepen our understanding of theoretical concepts.\n\n'
     'Secondly, it would be beneficial if we could have more group discussion sessions, through which we can exchange ideas and learn from each other.\n\n'
     'I would appreciate it if you could take my suggestions into account.\n\nYours sincerely,\nLi Ming'),

    # 投诉信 x3
    ('small', '【投诉信】产品质量', 1,
     'Dear Sir or Madam,\n\nI am writing to express my dissatisfaction with the electronic dictionary I purchased from your online store on July 15.\n\n'
     'Unfortunately, the product does not function as expected. The screen frequently freezes, and the battery drains within two hours of full charge.\n\n'
     'I would appreciate it if you could arrange a full refund or send a replacement as soon as possible. I have attached a copy of my receipt.\n\n'
     'I look forward to your prompt reply.\n\nYours sincerely,\nLi Ming'),
    ('small', '【投诉信】快递服务', 1,
     'Dear Sir or Madam,\n\nI am writing to complain about the express delivery service provided by your company.\n\n'
     'Last week, I sent an important document through your service, which was supposed to arrive within three days. However, after a week, the recipient still has not received it.\n\n'
     'I request that you investigate this matter immediately and provide compensation for the delay.\n\nYours sincerely,\nLi Ming'),
    ('small', '【投诉信】酒店体验', 1,
     'Dear Manager,\n\nI am writing to express my disappointment with my recent stay at your hotel from August 10 to August 13.\n\n'
     'The room was not properly cleaned, with stains on the carpet and an unpleasant odor. The air conditioning was also out of order.\n\n'
     'Given these circumstances, I believe I am entitled to a partial refund. I hope you will address these issues promptly.\n\nYours sincerely,\nLi Ming'),

    # 邀请信 x3
    ('small', '【邀请信】毕业典礼', 1,
     'Dear Professor Smith,\n\nI am writing to invite you to our graduation ceremony, which will be held on June 20 at the University Auditorium.\n\n'
     'The ceremony will begin at 9:00 a.m. and will include speeches, the awarding of degrees, and a photo session. Your presence would mean a great deal to all of us graduates.\n\n'
     'Please let me know by June 15 whether you will be able to attend. I sincerely hope you can join us.\n\nYours sincerely,\nLi Ming'),
    ('small', '【邀请信】学术讲座', 1,
     'Dear Professor,\n\nOn behalf of the Student Union, I am writing to invite you to deliver a lecture on Artificial Intelligence and Its Social Implications.\n\n'
     'The lecture is scheduled for September 15 at 2:00 p.m. in Lecture Hall 3. Given your expertise in this field, we believe your insights would greatly inspire our students.\n\n'
     'We would be honored if you could accept this invitation. Please inform us of your availability.\n\nYours sincerely,\nLi Ming'),
    ('small', '【邀请信】志愿者活动', 1,
     'Dear Fellow Students,\n\nI am writing to invite you to participate in our volunteer activity at the local nursing home this Saturday.\n\n'
     'We will depart at 8:30 a.m. and return by 4:00 p.m. Activities include chatting with the elderly, performing short plays, and helping with daily chores.\n\n'
     'If you are interested, please sign up by Friday noon at the Student Union office.\n\nYours sincerely,\nLi Ming'),

    # 感谢信 x2
    ('small', '【感谢信】感谢指导', 1,
     'Dear Professor Wang,\n\nI am writing to express my heartfelt gratitude for your patient guidance on my graduation thesis.\n\n'
     'Your insightful feedback and constructive suggestions were instrumental in helping me overcome numerous challenges. Without your help, I would not have been able to complete this work.\n\n'
     'I truly appreciate your dedication and the time you invested.\n\nYours sincerely,\nLi Ming'),
    ('small', '【感谢信】感谢款待', 1,
     'Dear Mr. and Mrs. Johnson,\n\nI am writing to thank you for your warm hospitality during my visit to your home last week.\n\n'
     'The delicious meals you prepared and the comfortable accommodations made my stay truly memorable. I especially enjoyed our conversations about cultural differences.\n\n'
     'I hope to have the opportunity to reciprocate your kindness when you visit China in the future.\n\nYours sincerely,\nLi Ming'),

    # 道歉信 x2
    ('small', '【道歉信】失约道歉', 1,
     'Dear Tom,\n\nI am writing to sincerely apologize for missing our appointment last Friday afternoon.\n\n'
     'I was unexpectedly called into a meeting with my supervisor that lasted much longer than anticipated, and I regret that I was unable to notify you in time.\n\n'
     'I would like to make it up to you by treating you to dinner this weekend. Please let me know what time works best.\n\nYours sincerely,\nLi Ming'),
    ('small', '【道歉信】损坏物品', 1,
     'Dear Jenny,\n\nI am writing to apologize for accidentally breaking your favorite coffee mug that you lent me last week.\n\n'
     'I feel terrible about this, as I know how much it meant to you. Please allow me to buy you a replacement.\n\n'
     'I promise to be more careful with borrowed items in the future. Once again, I am truly sorry.\n\nYours sincerely,\nLi Ming'),

    # 求职信 x2
    ('small', '【求职信】实习申请', 1,
     'Dear Sir or Madam,\n\nI am writing to apply for the summer internship position at your company, as advertised on the university career website.\n\n'
     'I am currently a junior majoring in Labor and Social Security at Jilin University. Through my coursework, I have developed strong analytical skills and proficiency in data analysis using Python and SPSS.\n\n'
     'I believe my academic background and practical experience make me a suitable candidate. I have attached my resume for your review.\n\n'
     'Thank you for your consideration.\n\nYours sincerely,\nLi Ming'),
    ('small', '【求职信】兼职申请', 1,
     'Dear Manager,\n\nI am writing to express my interest in the part-time tutor position advertised on the campus bulletin board.\n\n'
     'I am a third-year student with excellent academic records, especially in mathematics and English. I have one year of tutoring experience.\n\n'
     'I am patient, responsible, and good at explaining complex concepts in simple terms. I am available on weekday evenings and weekends.\n\n'
     'I look forward to hearing from you.\n\nYours sincerely,\nLi Ming'),

    # ===== LARGE ESSAYS (大作文) =====
    # 柱状图 x3
    ('large', '【柱状图】考研报名人数变化', 1,
     'As is clearly shown in the bar chart, the number of postgraduate exam applicants in China experienced a dramatic increase from 2.9 million in 2020 to 4.7 million in 2024.\n\n'
     'Several factors may contribute to this phenomenon. First and foremost, the increasingly competitive job market has driven more graduates to pursue higher degrees. '
     'Secondly, government policies encouraging higher education have also played a role, as many universities have expanded their postgraduate program enrollment.\n\n'
     'From my perspective, this trend is likely to continue in the foreseeable future. Therefore, we should face this competition with adequate preparation and a positive attitude.'),
    ('large', '【柱状图】大学生月消费构成', 1,
     'The bar chart presents the monthly consumption patterns of college students in 2023. As can be seen, food and catering account for the largest share at 45%, followed by entertainment at 20%. Books represent only 10%.\n\n'
     'The data reflects several noteworthy trends. The high proportion of food expenditure is understandable. However, the low spending on books is concerning, suggesting students may not be investing enough in intellectual development.\n\n'
     'In conclusion, while it is natural to spend on basic needs, students should strike a better balance and allocate more resources to learning.'),
    ('large', '【柱状图】各年级学习时间对比', 1,
     'The bar chart illustrates the changes in the average weekly study hours of college students across four academic years. Study hours declined from 35 hours in the freshman year to merely 18 hours in the senior year.\n\n'
     'Three reasons may explain this decline. As students progress, they take on more internships and part-time jobs. Senior students also allocate significant time to job hunting and graduate school applications.\n\n'
     'Based on the analysis, I suggest that students manage their time more effectively throughout college to ensure consistent academic engagement.'),

    # 折线图 x3
    ('large', '【折线图】城镇居民收入变化', 1,
     'The line graph illustrates the changes in the average income of urban residents in China from 2010 to 2023. As can be seen, the figure experienced a steady increase from 19,000 yuan to 49,000 yuan, a more than 2.5-fold growth.\n\n'
     'There are several reasons behind this growth. China sustained rapid economic development, creating abundant job opportunities. The government also raised the minimum wage standard several times.\n\n'
     'Based on the analysis, the living standards of urban residents have significantly improved. However, we should also note the widening income gap that requires policy attention.'),
    ('large', '【折线图】智能手机用户增长', 1,
     'The line graph depicts the trend of smartphone users in a certain region from 2015 to 2025. The number rose dramatically from 50 million to 380 million, particularly surging after 2019 with the introduction of 5G.\n\n'
     'This growth can be attributed to technological advancements making smartphones more affordable, and the proliferation of mobile applications turning smartphones into indispensable tools.\n\n'
     'In conclusion, the smartphone penetration rate will likely reach saturation soon, but technological innovation will continue to drive the industry forward.'),
    ('large', '【折线图】文理科专业招生对比', 1,
     'The line graph compares the enrollment numbers of Computer Science and History over ten years. While Computer Science enrollment surged from 200 to 1,200, History enrollment remained stable at around 300.\n\n'
     'The divergence can be explained by labor market demands. The booming IT industry has created strong demand for computer professionals, while History does not offer the same economic returns.\n\n'
     'From my perspective, while choosing majors with good job prospects is rational, we should not overlook the importance of humanities education for a well-rounded society.'),

    # 饼图 x2
    ('large', '【饼图】中国能源结构', 1,
     'The pie chart presents the proportion of different energy sources in China electricity generation in 2023. Coal accounts for the largest share at 56%, followed by renewable energy at 28%. Nuclear and natural gas represent 10% and 6% respectively.\n\n'
     'The data reflects China ongoing energy transition. The share of coal has decreased from over 70% a decade ago, while renewable energy has grown rapidly.\n\n'
     'In conclusion, while progress has been made, continued investment in green technology is essential for achieving carbon neutrality by 2060.'),
    ('large', '【饼图】大学生时间分配', 1,
     'The pie chart illustrates how college students allocate their daily 24 hours. Sleep takes up the largest portion at 33%, classes at 25%, self-study at 15%, and entertainment at 27%.\n\n'
     'The data reveals both positive and concerning aspects. Students prioritize adequate sleep, which is crucial for health. However, the limited time on self-study suggests many students need to improve time management.\n\n'
     'I believe students should increase self-study time to at least 20% of their daily schedule to ensure academic success.'),

    # 观点论证 x3
    ('large', '【观点论证】大学体育课是否必修', 1,
     'When it comes to whether university students should be required to take PE courses, opinions vary. Some believe PE should be optional, while others argue it should be mandatory. I strongly support the latter.\n\n'
     'First, regular exercise is essential for health. Studies show students who exercise regularly have better concentration and lower stress. Secondly, PE courses teach teamwork and perseverance.\n\n'
     'Admittedly, some students find PE burdensome given their heavy workload. However, two hours a week is not unreasonable.\n\n'
     'In conclusion, physical education should remain compulsory. After all, a sound mind resides in a sound body.'),
    ('large', '【观点论证】AI对社会的影响', 1,
     'The question of whether artificial intelligence will ultimately benefit or harm society has sparked heated debate. Some fear AI will displace workers, while others believe it will create more opportunities. I agree with the latter.\n\n'
     'History shows that technological revolutions ultimately create more jobs than they eliminate. Furthermore, AI can help solve pressing global challenges from disease diagnosis to energy optimization.\n\n'
     'Admittedly, the transition will be painful. Governments must invest in retraining programs. However, the long-term benefits outweigh the costs.\n\n'
     'In conclusion, we should embrace AI with cautious optimism, ensuring its benefits are shared widely.'),
    ('large', '【观点论证】大学生是否应该创业', 1,
     'Should college students start their own businesses while still in school? Some consider it a valuable learning experience, while others argue it distracts from academic pursuits. I side with the former.\n\n'
     'Firstly, entrepreneurship cultivates practical skills that classrooms cannot teach. Running a business requires financial management, marketing, and problem-solving. Secondly, even if the venture fails, the experience is invaluable.\n\n'
     'Of course, students must strike a balance. Entrepreneurship should complement, not replace, academic learning.\n\n'
     'In summary, campus entrepreneurship, when approached responsibly, is an excellent way to prepare for the real world.'),

    # 原因分析 x2
    ('large', '【原因分析】年轻人阅读量下降', 1,
     'In recent years, there has been a growing concern over declining reading habits among young people. Surveys indicate college students average reading time has dropped to less than 30 minutes per day.\n\n'
     'Several factors account for this. First, short-form video platforms like Douyin have fundamentally changed how young people consume information. Second, increasing academic pressures leave little leisure time. Finally, the lack of a reading culture on campus also contributes.\n\n'
     'To address this, universities should organize book clubs, and parents should set an example at home. Only through joint efforts can we revive the joy of reading.'),
    ('large', '【原因分析】大学生心理健康问题', 1,
     'The increasing prevalence of mental health issues among college students has become a pressing concern. Reports indicate over 30% of Chinese college students show signs of anxiety or depression.\n\n'
     'Several factors contribute to this trend. Primarily, intense academic competition creates enormous pressure. Additionally, the transition from home to campus life can be overwhelming. The stigma surrounding mental health also prevents many from seeking help.\n\n'
     'To address this crisis, universities should establish accessible counseling services and integrate mental health education into the curriculum from an early age.'),

    # 利弊分析 x2
    ('large', '【利弊分析】大学生使用社交媒体', 1,
     'The issue of whether college students should use social media has been brought to public attention recently. Like a double-edged sword, it brings both advantages and disadvantages.\n\n'
     'On the one hand, social media enables students to stay connected, access educational content, and build professional networks. On the other hand, excessive use can lead to addiction and reduced attention span.\n\n'
     'In conclusion, social media itself is neither good nor bad. Setting time limits and using it mindfully can maximize benefits while avoiding pitfalls.'),
    ('large', '【利弊分析】在线教育的利弊', 1,
     'Online education has experienced explosive growth in recent years. However, opinions remain divided on its effectiveness compared to traditional learning.\n\n'
     'On the one hand, online education offers unprecedented flexibility. Students can learn at their own pace and access courses from top universities. On the other hand, online learning lacks face-to-face interaction and requires strong self-discipline.\n\n'
     'In conclusion, the optimal approach may be a blended model that combines the flexibility of online learning with the personal touch of traditional classrooms.'),
]

for etype, title, is_template, content in templates:
    db.execute('INSERT INTO writing_essays (type, title, content, created_at, is_template) VALUES (?,?,?,?,?)',
               (etype, title, content, now, is_template))

db.commit()

small = db.execute("SELECT COUNT(*) FROM writing_essays WHERE type='small' AND is_template=1").fetchone()[0]
large = db.execute("SELECT COUNT(*) FROM writing_essays WHERE type='large' AND is_template=1").fetchone()[0]
print(f'{small} small + {large} large = {small+large} templates total')
db.close()

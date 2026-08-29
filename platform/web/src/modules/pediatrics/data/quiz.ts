import type { QuizItem } from './types'

/**
 * 自测题库 — 全部题目出自《程氏家传儿科秘要》及附编《幼科铁镜》。
 * 分类：八症辨证 / 方药 / 歌诀诊法 / 图谱辨识 / 危候 / 训诫推拿
 */
const B = '八症辨证'
const F = '方药'
const G = '歌诀诊法'
const T = '图谱辨识'
const W = '危候'
const X = '训诫推拿'

export const quizBank: QuizItem[] = [
  // ===== 八症辨证 =====
  { id: 'bz01', category: B, type: 'single', question: '程氏八症不包括下列哪一项？', options: ['风热', '急惊风', '麻疹', '燥火'], answer: [2], explain: '八症为：风热、急惊风、慢惊风、慢脾风、脾虚、疳积、燥火、咳嗽。麻疹见"三症录验"附篇。', source: '释八症六字说' },
  { id: 'bz02', category: B, type: 'single', question: '治法六字指：', options: ['平肝、补脾、泻心', '祛风、清热、化痰', '解表、清里、和中', '补气、养血、滋阴'], answer: [0], explain: '六字：平肝、补脾、泻心。', source: '释八症六字说' },
  { id: 'bz03', category: B, type: 'single', question: '小儿体质三大特点（染病多由此致）是：', options: ['肝常有余、脾常不足、心火常炎', '肺常不足、肾常虚、脾常有余', '心常有余、肝常不足、肺常虚', '阳常有余、阴常不足、肾常虚'], answer: [0], explain: '小儿肝常有余、脾常不足、心火常炎。', source: '释八症六字说' },
  { id: 'bz04', category: B, type: 'single', question: '风热证的病机是：', options: ['肝木心火相搏', '肝木克脾土', '心火克肺金', '脾虚生湿'], answer: [0], explain: '肝木主风、心火主热，二经相搏则成风热，治法平肝泻心。', source: '释八症六字说' },
  { id: 'bz05', category: B, type: 'single', question: '风热证外候之"泻青黄色如浮萍状"的病机是：', options: ['肝木旺克脾土', '心火下迫小肠', '肺热移于大肠', '肾虚不固'], answer: [0], explain: '肝木色青、脾土色黄，肝木旺克脾土故泻青黄色；不泻者是脾土未受肝克。', source: '一、风热治法' },
  { id: 'bz06', category: B, type: 'multi', question: '风热证的手纹脉象特征（多选）：', options: ['手纹浮紫', '左手纹常浮于右手', '脉浮数', '纹沉而青'], answer: [0, 1, 2], explain: '纹浮为风在表、紫为热；左手主肝故浮；脉浮数。纹沉而青是慢惊之候。', source: '一、风热治法' },
  { id: 'bz07', category: B, type: 'single', question: '急惊即"风热夹惊"，其标志性外候是：', options: ['睡中心常跳动、手足常惕、目直视上视、痰鸣如锯', '手足冷、吐泻不止', '面黄肌瘦、肚大青筋', '干咳无痰、夜间热增'], answer: [0], explain: '急惊在风热外候之上，加惊惕、抽掣、直视、咬牙、痰鸣如锯。', source: '二、急惊治法' },
  { id: 'bz08', category: B, type: 'single', question: '急惊"喉中痰鸣如锯"属：', options: ['风痰壅于喉间', '肺气将绝', '胃气上逆', '肾不纳气'], answer: [0], explain: '风塞则痰升，此风痰也，在喉间停滞不散故有此声。失治不险，痰消而症即愈。', source: '二、急惊治法' },
  { id: 'bz09', category: B, type: 'single', question: '慢惊多由何而来？', options: ['急惊失治迁延传里', '外感风寒直中', '先天胎毒', '饮食不洁'], answer: [0], explain: '多由急惊失治、迁延日久传里而成，亦有起而即成者（内生风），但急惊传慢惊者居多。', source: '三、慢惊症治' },
  { id: 'bz10', category: B, type: 'single', question: '慢惊"手足冷"的病机是：', options: ['肝风入内克脾、脾气受克不通四肢', '寒邪束表', '阳气暴脱', '血虚不荣'], answer: [0], explain: '脾主四肢，脾气受克不通四肢故手足冷。', source: '三、慢惊症治' },
  { id: 'bz11', category: B, type: 'single', question: '慢惊预后的关键判断是：', options: ['此病务由吐泻方为病退；有身热者难治、无身热者易治', '汗出者必死', '脉数者易治', '口渴者必愈'], answer: [0], explain: '吐泻止为病退；身热者脾虚热甚两难，唯川连厚肠退热可用。', source: '三、慢惊症治' },
  { id: 'bz12', category: B, type: 'multi', question: '慢惊之死候包括（多选）：', options: ['泻不止、眼眶深陷、气喘不定', '干呕无物', '气喘（胃气欲散）', '手足温、脉有力'], answer: [0, 1, 2], explain: '肝克脾、肝风动故死；干呕无物者胃气绝也死。', source: '三、慢惊症治' },
  { id: 'bz13', category: B, type: 'single', question: '慢脾风较慢惊更甚之处在于：', options: ['惊风病气已全传入脾，有惊惊无可去、有风风无可祛', '身热更重', '抽搐更频', '咳嗽更剧'], answer: [0], explain: '此时唯大补脾胃、涩肠止泻一法。', source: '四、慢脾风症' },
  { id: 'bz14', category: B, type: 'single', question: '慢脾风第一要务是：', options: ['止泻', '退热', '化痰', '安神'], answer: [0], explain: '慢脾急症必要以止泻为重，泻止则各般症候亦渐减。', source: '言症论治' },
  { id: 'bz15', category: B, type: 'single', question: '慢脾风"脉微而不乱、重按至底迟而有力"提示：', options: ['元气尚藏，有望', '散脉难生', '邪气盛实', '热深厥深'], answer: [0], explain: '脉浮泛无力、离乱十余至而重按则无者为散脉，难望有生。', source: '四、慢脾风症' },
  { id: 'bz16', category: B, type: 'single', question: '脾虚证"左手脉略大于右手"提示：', options: ['木胜相克（肝乘脾）', '心火旺', '肺气虚', '肾水亏'], answer: [0], explain: '左寸心克右寸肺、左关肝克右关脾，木胜相克也。', source: '五、脾虚论治' },
  { id: 'bz17', category: B, type: 'multi', question: '脾虚小儿可见的兼症（多选）：', options: ['潮热、暮热', '盗汗、自汗', '变生慢惊慢脾', '疳症、水肿、痰'], answer: [0, 1, 2, 3], explain: '种种病端皆由脾虚而得，故脾虚小儿当无病时最宜调理脾胃。', source: '五、脾虚论治' },
  { id: 'bz18', category: B, type: 'single', question: '五疳中"面黄肌瘦、肚大筋青、食多不化"属：', options: ['脾疳', '肝疳', '心疳（惊疳）', '肾疳'], answer: [0], explain: '肝疳善哭善怒咬指；心疳多烦惊头生小疮；肺疳咳喘鼻疮；肾疳囟陷目无光骨软迟行。', source: '六、疳症诠治' },
  { id: 'bz19', category: B, type: 'single', question: '疳症的两大总因是：', options: ['脾虚食滞、肝火气郁', '外感风寒、内伤饮食', '先天不足、后天失养', '心火亢盛、肺金受灼'], answer: [0], explain: '总不外乎脾虚食滞、肝火气郁二大端，治以平肝补脾去积。', source: '六、疳症诠治' },
  { id: 'bz20', category: B, type: 'single', question: '燥火证"阳症似阴"的表现是：', options: ['冷热时作、手足时冷时热、食入即吐、神昏目闭如醉人', '面色苍白、四肢厥冷', '大便清稀、小便清长', '舌淡脉微'], answer: [0], explain: '此是伏热在内不能宣通，仍是热症，易误认阴症。', source: '七、小儿燥火' },
  { id: 'bz21', category: B, type: 'single', question: '燥火证手纹特点是：', options: ['两手纹粗大而紫；伏热者纹隐约而滞、一截一截', '纹沉而青', '纹淡红生毛', '纹隐现无常'], answer: [0], explain: '纹粗大而紫为热盛浮露；一截一截模糊为伏热。', source: '七、小儿燥火' },
  { id: 'bz22', category: B, type: 'single', question: '燥火脉象"左手甚于右手为重"的道理是：', options: ['左属心肝、木火相生，相克为轻、相生为重', '左手脉本大', '左主表', '左候气分'], answer: [0], explain: '左手甚于右手为重，右手甚于左手为轻（相克不相克也）。', source: '七、小儿燥火' },
  { id: 'bz23', category: B, type: 'single', question: '"有声无痰谓之咳"的病机是：', options: ['火燥肺经', '气动脾胃之湿', '痰火气动', '肝风犯肺'], answer: [0], explain: '有痰无声谓之嗽（脾胃之湿）；有痰有声谓之咳嗽。', source: '八、咳嗽症' },
  { id: 'bz24', category: B, type: 'single', question: '咳嗽证"右手纹必浮于左手"是因为：', options: ['右手纹主肺', '右手主脾', '右手候气', '右手主表'], answer: [0], explain: '病儿若现此纹有咳无疑，右手纹主肺故也。', source: '八、咳嗽症' },
  { id: 'bz25', category: B, type: 'multi', question: '咳嗽的五类分型（多选）：', options: ['风热之咳', '燥火之咳', '惊痰之咳', '食痰之咳、乳痰之咳（吼症）'], answer: [0, 1, 2, 3], explain: '五类各有外候与手纹脉象之凭。', source: '八、咳嗽症' },
  { id: 'bz26', category: B, type: 'single', question: '乳痰吼症（百日咳）最重者的发病时间是：', options: ['出世百日而出者（马上紧痉）', '半岁而出', '一岁而出', '三岁而出'], answer: [0], explain: '当小儿出世百日而出者名马上紧痉，即百日咳，最重。', source: '八、咳嗽症' },
  { id: 'bz27', category: B, type: 'single', question: '因咳而喘与惊风之喘的区别是：', options: ['因咳而喘属肺受痰火，病虽喘亦无碍；肝风夹惊之喘为胃气欲脱之危候', '二者无区别', '因咳而喘必死', '惊风之喘易治'], answer: [0], explain: '肝木克脾气、胃气欲脱而喘者则危候也。', source: '八、咳嗽症' },
  { id: 'bz28', category: B, type: 'single', question: '咳嗽治法中"理脾"的意义是：', options: ['补土生金（隔一之治）', '脾主运化水湿', '脾为后天之本', '以上皆是'], answer: [3], explain: '理脾以生肺气，亦隔一而言，补土生金。', source: '八、咳嗽症' },
  { id: 'bz29', category: B, type: 'single', question: '八症总论：疳症又病惊风，当如何参治？', options: ['以惊风、疳症两则一同参看', '只治惊风', '只治疳症', '按古方另立方'], answer: [0], explain: '两则同见宜兼同参治。', source: '八症总论' },
  { id: 'bz30', category: B, type: 'single', question: '各方为"方底"的含义是：', options: ['药味未齐，必有照此方后加法加入方底内，然后药性始齐', '方剂已完备', '只是参考不可用', '底方需另开丸散'], answer: [0], explain: '各病条下均立一方者，确"方底"耳。', source: '八症总论' },
  { id: 'bz31', category: B, type: 'single', question: '疟疾之邪所聚之经是：', options: ['少阳（半表半里）', '太阳', '阳明', '太阴'], answer: [0], explain: '外湿引内邪聚于少阳之经，阴阳交争则寒热往来。', source: '疟疾论治' },
  { id: 'bz32', category: B, type: 'single', question: '暑症转筋（霍乱转筋）的治法：', options: ['脾虚用六和汤、实症用香薷饮加重木瓜', '大承气汤', '麻黄汤', '补中益气汤'], answer: [0], explain: '治亦平肝补脾之法，因肝主筋、肝木犯胃。', source: '暑症论治' },
  { id: 'bz33', category: B, type: 'single', question: '痢症治法最忌：', options: ['利小便（小便利则干涸大肠）', '行气', '平肝', '补脾'], answer: [0], explain: '最忌利小便。初起要推利使积不留滞，通因通用。', source: '痢症论治' },
  { id: 'bz34', category: B, type: 'single', question: '痢色黄、白、红所主之脏：', options: ['黄者脾热传大肠、白者肺热传大肠、红者心热传大肠', '黄者肝、白者肾、红者心', '黄者胃、白者肺、红者脾', '不分脏腑'], answer: [0], explain: '各色分经而治。', source: '痢症论治' },
  { id: 'bz35', category: B, type: 'single', question: '看外症法：唇色"深红而亮"主：', options: ['风热', '实热', '脾胃虚寒', '湿热'], answer: [0], explain: '红而焦暗为实热；淡白为脾胃虚寒；黄淡暗为湿热；枯白如朽骨为脾绝。', source: '看外症法' },
  { id: 'bz36', category: B, type: 'single', question: '看外症法：眼白青蓝色主：', options: ['肝有风', '肾虚', '肺火', '湿热'], answer: [0], explain: '肝开窍于目，青蓝为肝风。', source: '看外症法' },
  { id: 'bz37', category: B, type: 'single', question: '看外症法：发竖向上（直指向天）最常见的原因是：', options: ['乳母有胎、儿食孕乳（喜病）', '先天肾气足', '肝血旺', '风热在表'], answer: [0], explain: '可速嘱其断乳；若无此故而发如此者，则急死之症也。', source: '看外症法' },
  { id: 'bz38', category: B, type: 'single', question: '问诊法：渴而饮冷主：', options: ['内湿热', '内热、风热传里', '脾胃虚寒', '水停胸中'], answer: [0], explain: '渴而饮热者为内热、为风热传里。', source: '问诊法' },
  { id: 'bz39', category: B, type: 'single', question: '问诊法：小便落地即结为白浆主：', options: ['大湿热', '无热', '肾虚', '脾虚'], answer: [0], explain: '短黄为有热湿火；长白为无热。', source: '问诊法' },
  { id: 'bz40', category: B, type: 'single', question: '小儿脉较成人：', options: ['多加两至看（纯阳之体脉息常数）', '少两至', '相同', '无定数'], answer: [0], explain: '脉数一息八九至、脉迟一息五六至，与大人不同。', source: '切脉法' },

  // ===== 方药 =====
  { id: 'fy01', category: F, type: 'single', question: '第一方（风热）中"泻心火"之药是：', options: ['木通', '羌活', '防风', '薄荷'], answer: [0], explain: '木通二钱泻心火；生栀二钱平肝火；川地骨退身热。', source: '第一方' },
  { id: 'fy02', category: F, type: 'single', question: '第二方（急惊）中"去肝风、治抽掣"之主药是：', options: ['钩藤', '柴胡', '连翘', '蝉蜕'], answer: [0], explain: '钩藤一钱去肝风治抽掣；大抽掣加全蝎。', source: '第二方' },
  { id: 'fy03', category: F, type: 'single', question: '第三方（慢惊）治身热泄泻而"不碍补脾止泻"之药是：', options: ['川连（姜汁炒）', '石膏', '大黄', '羚羊角'], answer: [0], explain: '唯有身热泄泻者用川连，能厚肠退热，不碍补脾止泻之功。', source: '第三方' },
  { id: 'fy04', category: F, type: 'multi', question: '第四方（慢脾风）组成包括（多选）：', options: ['米党参、白术、茯苓', '陈皮、炙甘草', '焦芍、僵蚕、钩藤', '白附子'], answer: [0, 1, 2, 3], explain: '此为异功散加味补脾的首方，加伏龙肝煎。', source: '第四方' },
  { id: 'fy05', category: F, type: 'single', question: '第五方（脾虚）即：', options: ['加味六神散', '四君子汤', '异功散', '参苓白术散'], answer: [0], explain: '六神散加陈皮、山楂、神曲、白芍；前人用治疳积屡试皆验。', source: '第五方' },
  { id: 'fy06', category: F, type: 'single', question: '第六方（疳积）中"开胃化食积"之药是：', options: ['莪术', '柴胡', '郁金', '茯苓'], answer: [0], explain: '莪术最消食积又不伤胃（用药秘验杂说）。', source: '第六方' },
  { id: 'fy07', category: F, type: 'multi', question: '第七方（燥火）组成（多选）：', options: ['川连、知母、黄芩', '元参、龙胆草', '木通、犀角', '甘草、灯芯'], answer: [0, 1, 2, 3], explain: '治小儿燥火总剂，按各经加味治之。', source: '第七方' },
  { id: 'fy08', category: F, type: 'single', question: '第八方（咳嗽）中"下气、清热、去痰"之药是：', options: ['款冬花', '前胡', '桔梗', '桑白皮'], answer: [0], explain: '款冬花二钱下气清热去痰；夹惊者款冬倍用。', source: '第八方' },
  { id: 'fy09', category: F, type: 'single', question: '导赤散主治：', options: ['心火、心与小肠之火（小便短赤）', '肝火', '胃火', '肾火'], answer: [0], explain: '泻心火、泻心与小肠之火。', source: '官方验方' },
  { id: 'fy10', category: F, type: 'single', question: '六味地黄丸分量歌："地八、山山四、丹泽苓用三"指：', options: ['熟地八钱、淮山山萸各四钱、丹皮泽泻茯苓各三钱', '生地八钱、山药山茱萸各三钱', '熟地八两', '以上皆非'], answer: [0], explain: '熟地八钱、淮山四钱、白茯苓三钱、丹皮三钱、泽泻三钱、山萸四钱。', source: '官方验方' },
  { id: 'fy11', category: F, type: 'single', question: '四苓散加何药名五苓散？', options: ['桂枝', '肉桂', '附子', '干姜'], answer: [0], explain: '白术、猪苓、赤苓、泽泻，加桂名五苓散。', source: '官方验方' },
  { id: 'fy12', category: F, type: 'single', question: '宣风散热散主治：', options: ['热极大便不通（胜用大黄承气、不伤元气）', '风寒表证', '脾虚泄泻', '咳嗽痰多'], answer: [0], explain: '丹溪常用治瘟症，程氏加元明粉治热闭甚效。', source: '官方验方' },
  { id: 'fy13', category: F, type: 'multi', question: '加味冰硼散治口内诸症，急症加味包括（多选）：', options: ['朴硝、山豆根、青黛', '牛黄、珍珠', '人中白、川连', '地猪（鼠妇）'], answer: [0, 1, 2, 3], explain: '喉内百般怪症紧急者加味吹喉；火热毒急症加地猪（鼠妇）。', source: '官方验方' },
  { id: 'fy14', category: F, type: 'single', question: '玉屏风散组成：', options: ['北芪、白术、防风', '黄芪、当归、桂枝', '白术、茯苓、甘草', '防风、荆芥、薄荷'], answer: [0], explain: '固表止汗。', source: '官方验方' },
  { id: 'fy15', category: F, type: 'single', question: '治疟总剂是：', options: ['小柴胡汤加减', '补中益气汤', '六和汤', '导赤各半汤'], answer: [0], explain: '加川朴、淡竹叶、猪苓、草果、常山。', source: '疟疾论治' },
  { id: 'fy16', category: F, type: 'single', question: '发冷敷脐法所用：', options: ['草果仁、北辛、牙皂、苍术、鹿耳铃为末，酒润和鸡蛋煎饼贴脐', '胡椒丁香玉桂饼', '赤石脂五倍子糊', '麻黄根龙骨牡蛎末'], answer: [0], explain: '未发时贴肚脐，以带束紧。', source: '疟疾外治' },
  { id: 'fy17', category: F, type: 'single', question: '暑症之"治暑方底"是：', options: ['香薷饮', '六和汤', '生脉散', '白虎汤'], answer: [0], explain: '香薷一钱、川朴一钱、扁豆三钱、木瓜钱半，加灯芯草，开甘泉散。', source: '暑症备用方' },
  { id: 'fy18', category: F, type: 'single', question: '暑症"泄泻"之加味中程氏家秘之品是：', options: ['冬瓜仁', '木瓜', '扁豆', '香薷'], answer: [0], explain: '甚则加冬瓜仁，此味家秘。', source: '暑症备用方' },
  { id: 'fy19', category: F, type: 'single', question: '着暑后神昏目闭如醉人（暑邪传心）之方是：', options: ['导赤各半汤', '六和汤', '香薷饮', '清暑益气汤'], answer: [0], explain: '暑邪传入心经、心火上逼肺故也，如伤寒越经之法治之，百发百中。', source: '着暑后二难症' },
  { id: 'fy20', category: F, type: 'multi', question: '出麻备用方组成包括（多选）：', options: ['荆芥、防风、银花', '桔梗、知母、石膏', '山楂、连翘、牛子', '地丁、黄芩、木通'], answer: [0, 1, 2, 3], explain: '治麻以凉血、托口、解暑湿、清心脾胃之火为要。', source: '出麻备用方' },
  { id: 'fy21', category: F, type: 'single', question: '麻疹色红暗（血热）加：', options: ['生地、赤芍、丹皮，开玉露散', '川连、羚羊', '荆芥、苏叶', '防党、苡仁'], answer: [0], explain: '气弱麻色淡滞出不快者加防党、苡仁，去山楂、石膏。', source: '出麻备用方' },
  { id: 'fy22', category: F, type: 'single', question: '白痱子与麻疹的分属：', options: ['白痱子属气分为轻、麻疹属血分为重', '白痱子属血分、麻疹属气分', '相同', '皆属肺胃湿'], answer: [0], explain: '二症缘自肺、胃二经之湿而出。', source: '出白痱子方' },
  { id: 'fy23', category: F, type: 'multi', question: '痢症方组成（多选）：', options: ['川朴、山楂、神曲', '白芍、黄芩、甘草', '川连、木香', '伏龙肝（煎引）'], answer: [0, 1, 2, 3], explain: '加伏龙肝煎，开胃苓散、转笑散。', source: '痢症方' },
  { id: 'fy24', category: F, type: 'single', question: '慢脾风止泻贴脐法所用三味：', options: ['胡椒、丁香、玉桂', '附子、干姜、肉桂', '花椒、茴香、吴萸', '麝香、冰片、樟脑'], answer: [0], explain: '为末入灰面烧酒搓饼，一枚贴脐、两枚贴两足肚。', source: '第四方外治' },
  { id: 'fy25', category: F, type: 'single', question: '止汗外扑法所用：', options: ['麻黄根、龙骨、牡蛎共末扑之', '滑石粉', '冰硼散', '玉屏风散'], answer: [0], explain: '以绢布或纱袋装此末，向有汗处扑之如敷粉状。', source: '第四方外治' },
  { id: 'fy26', category: F, type: 'single', question: '丸散中"大去壮热实热"者是：', options: ['玉露散', '胃苓散', '慢惊散', '转笑散'], answer: [0], explain: '退热则用玉露散，大去壮热实热。', source: '用药秘验杂说' },
  { id: 'fy27', category: F, type: 'single', question: '丸散中"为最止泻"者是：', options: ['慢惊散', '保婴丹', '万灵丹', '急惊散'], answer: [0], explain: '慢惊散为最止泻，因脾虚必以补脾药为底子。', source: '用药秘验杂说' },
  { id: 'fy28', category: F, type: 'single', question: '消食之药不应（积滞已成）时，程氏改用：', options: ['莪术（最消食积又不伤胃）', '加大山楂量', '巴豆', '泻下峻剂'], answer: [0], explain: '配谷芽消食生胃气、川朴破滞，杏仁槟榔白术补消兼行。', source: '用药秘验杂说' },
  { id: 'fy29', category: F, type: 'single', question: '"食厥"（痰水潮心、状似惊风）的正确治法：', options: ['四君子汤加川朴、尖槟、砂仁、莪术、半夏、桔梗醒脾', '大剂惊风药', '清热泻火', '安神定志'], answer: [0], explain: '误服惊风药不独不效且生燥热之患。', source: '用药秘验杂说' },
  { id: 'fy30', category: F, type: 'single', question: '顽积所用猛药（当慎用）：', options: ['干漆、芜荑、白矾', '人参、黄芪', '甘草、大枣', '薄荷、蝉蜕'], answer: [0], explain: '干漆、芜荑、蚊蛤（存疑）、白矾俱猛药，当慎用。', source: '用药秘验杂说' },
  { id: 'fy31', category: F, type: 'single', question: '脾虚泄泻用药不效，须兼用：', options: ['提气之药（干葛、柴胡、升麻）', '收敛涩肠', '温补肾阳', '消食导滞'], answer: [0], explain: '浊气在下则生飧泄，提清气而泻自止。', source: '用药秘验杂说' },
  { id: 'fy32', category: F, type: 'single', question: '石类药（石膏等）使用注意：', options: ['煅过出尽火气、以甘草制其毒，否则小便不通', '生用更佳', '无需炮制', '忌与甘草同用'], answer: [0], explain: '言症论治第十六条。', source: '言症论治' },
  { id: 'fy33', category: F, type: 'single', question: '先煎之药：', options: ['羚羊、犀角、石膏', '薄荷、木香、玉桂', '甘草、大枣', '蝉蜕、灯芯'], answer: [0], explain: '坚硬难出味者先煎；薄荷木香肉桂后下。', source: '言症论治' },
  { id: 'fy34', category: F, type: 'single', question: '立方药味之限：', options: ['以十二味为率，最多十四味', '越多越好', '以八味为限', '无限制'], answer: [0], explain: '多则杂乱不应。', source: '言症论治' },
  { id: 'fy35', category: F, type: 'single', question: '泻肺脾肾之凉药的使用戒律：', options: ['虽热症亦当慎用，过凉能脱元气', '可放心重用', '只用于成人', '配温药即可'], answer: [0], explain: '泻心肝药虽大凉无过寒之患；泻肺脾肾之凉须慎。', source: '用药秘验杂说' },

  // ===== 歌诀诊法 =====
  { id: 'gy01', category: G, type: 'single', question: '"小儿有病手纹浮，诸病因从表症求"——纹浮主：', options: ['表证', '里证', '虚证', '寒证'], answer: [0], explain: '浮为风、为病在表。', source: '手纹浮沉分表里歌' },
  { id: 'gy02', category: G, type: 'single', question: '"关纹见紫热为真，青色为风古所称"——纹色主病对应：', options: ['紫主热、青主风', '紫主风、青主热', '紫主寒、青主虚', '紫主虚、青主湿'], answer: [0], explain: '青紫若然难辨识，当看外候证来因。', source: '手纹青紫辨风热歌' },
  { id: 'gy03', category: G, type: 'single', question: '淡滞定虚实歌：纹淡主虚、纹滞主：', options: ['实', '寒', '热', '风'], answer: [0], explain: '指纹淡淡亦堪惊，总为先天赋禀轻。', source: '淡滞定虚实歌' },
  { id: 'gy04', category: G, type: 'single', question: '三关判安危："风轻、气重、命危"的出处与含义：', options: ['《水镜集》：纹在风关病轻、气关病重、命关病危', '程氏自创', '《幼幼集成》', '《内经》'], answer: [0], explain: '看指纹一法是宋人《水镜集》首创，"寅曰风关、卯曰气关、辰曰命关"。', source: '诊手纹法按语' },
  { id: 'gy05', category: G, type: 'single', question: '推视指纹的正确方法：', options: ['以拇指侧面（桡侧）推，从命关推向风关', '以指头正面推，从风关推向命关', '任意方向', '用指甲刮'], answer: [0], explain: '静脉由四肢走向心脏，反推会使血液郁于远端造成"纹透三关"的误判。', source: '诊手纹法按语' },
  { id: 'gy06', category: G, type: 'single', question: '小儿一息脉数至者平：', options: ['八九至（较成人多加两至）', '四五至', '十余至', '与成人相同'], answer: [0], explain: '纯阳之体脉息常数。', source: '切脉法' },
  { id: 'gy07', category: G, type: 'single', question: '"弹指如牵强状者"为何脉？', options: ['紧脉（为寒）', '数脉（为热）', '滑脉', '弦脉'], answer: [0], explain: '紧为寒；数为热，昭昭有应手者为数。', source: '切脉法' },
  { id: 'gy08', category: G, type: 'single', question: '两手脉沉滑主：', options: ['痰、食', '风痰', '虚', '热'], answer: [0], explain: '浮滑为风痰；有力为实无力为虚。', source: '切脉法' },
  { id: 'gy09', category: G, type: 'single', question: '看外症法望诊顺序（第一项）：', options: ['以一手按其额上，有无身热自然知之', '看唇色', '看舌', '看耳背'], answer: [0], explain: '次看唇、鼻、眼、舌、耳背、发、肚皮、肾囊，最后问证。', source: '看外症法' },
  { id: 'gy10', category: G, type: 'single', question: '耳背有纹的意义：', options: ['防其出痘疱，乱纹为凶、一条轻症', '主耳聋', '主肾虚', '主惊风'], answer: [0], explain: '三条次之、两条又次之、一条轻症。', source: '看外症法' },
  { id: 'gy11', category: G, type: 'single', question: '望肚皮："气胀如鼓、声如卜卜声（龟壳声）"主：', options: ['气郁有积', '儿壮', '膀胱停水', '死候'], answer: [0], explain: '皮薄筋露、气胀如鼓者为气郁有积。', source: '看外症法' },
  { id: 'gy12', category: G, type: 'single', question: '肾囊"光亮如琉璃装水状"主：', options: ['膀胱气弱、浸湿停水，治当补土利水', '儿壮', '肾气充足', '疝气'], answer: [0], explain: '软大长垂者为儿弱、为病重。', source: '看外症法' },
  { id: 'gy13', category: G, type: 'single', question: '问诊法：日夜俱热者为：', options: ['壮热、实热（风热则日夜俱热）', '虚热', '潮热', '暑热'], answer: [0], explain: '虚热内热则日轻夜重；潮热有时而作。', source: '问诊法' },
  { id: 'gy14', category: G, type: 'single', question: '问诊法：夜间睡着手足跳动主：', options: ['有惊', '脾虚', '肾虚', '肺热'], answer: [0], explain: '如有则为有惊。', source: '问诊法' },
  { id: 'gy15', category: G, type: 'single', question: '泻白如糊状而酸臭主：', options: ['伤食', '风热', '湿热', '脾胃虚寒'], answer: [0], explain: '青黄如浮萍为风热；净黄水为湿热；净白水为脾胃虚寒。', source: '问诊法' },
  { id: 'gy16', category: G, type: 'single', question: '泻白沫、红沫、黄沫分别主：', options: ['气分湿热、血分湿热、脾经湿热', '寒、热、虚', '风、寒、湿', '痰、食、积'], answer: [0], explain: '泻沫与"痢"字同一意义。', source: '问诊法' },
  { id: 'gy17', category: G, type: 'single', question: '"脾胃受湿、水停胸中、热蒸作渴"之圣药：', options: ['四苓散', '导赤散', '泻白散', '六味丸'], answer: [0], explain: '当利水开胸，四苓散为圣药。', source: '问诊法' },
  { id: 'gy18', category: G, type: 'single', question: '司天歌：子午之年何气司天？', options: ['少阴君火', '太阴湿土', '少阳相火', '阳明燥金'], answer: [0], explain: '子午少阴为君火；上半年君火之病多。', source: '司天歌' },
  { id: 'gy19', category: G, type: 'single', question: '天干合脏腑：甲属何脏何腑？', options: ['胆（阳木）', '肝（阴木）', '心（阴火）', '小肠（阳火）'], answer: [0], explain: '甲胆阳木、乙肝阴木、丙小肠阳火、丁心阴火。', source: '天干合脏腑相属歌' },
  { id: 'gy20', category: G, type: 'single', question: '五脏主病定例："主惊"之脏为：', options: ['心', '肝', '脾', '肺'], answer: [0], explain: '心主惊、肝主风、脾主困、肺主喘、肾主虚。', source: '五脏主病定例' },

  // ===== 图谱辨识 =====
  { id: 'tp01', category: T, type: 'single', question: '流珠形纹的特点与主病：', options: ['只一点红见于风关，主饮食所伤、内热欲吐', '三脉并行，主惊风食积', '纹直上，主风热', '大头向气关，主脾虚食积'], answer: [0], explain: '流珠一点红于风关。', source: '手纹十八图式' },
  { id: 'tp02', category: T, type: 'single', question: '环珠形主：', options: ['脾虚停食、胸膈胀满、烦渴发热', '感冒寒邪', '心肝热极生风', '肝木克脾土败证'], answer: [0], explain: '其点差大，圆环如珠。', source: '手纹十八图式' },
  { id: 'tp03', category: T, type: 'single', question: '来蛇形主：', options: ['脾胃湿热、中脘不利、干呕不食', '脾虚食积、吐泻烦渴', '惊风食积', '饮食所伤'], answer: [0], explain: '长散出气关，一头大一头尖。', source: '手纹十八图式' },
  { id: 'tp04', category: T, type: 'single', question: '去蛇形（大头向气关）主：', options: ['脾虚食积、吐泻烦渴', '脾胃湿热', '痰热', '风热'], answer: [0], explain: '来蛇去蛇方向相反，主病不同。', source: '手纹十八图式' },
  { id: 'tp05', category: T, type: 'single', question: '弓反里形主：', options: ['感冒寒邪', '痰热', '风热', '惊风'], answer: [0], explain: '弓反外形主痰热。', source: '手纹十八图式' },
  { id: 'tp06', category: T, type: 'single', question: '枪形（纹直上）主：', options: ['风热', '寒邪', '食积', '虚寒'], answer: [0], explain: '枪形直上，主风热。', source: '手纹十八图式' },
  { id: 'tp07', category: T, type: 'single', question: '鱼骨形（纹分支歧）主：', options: ['惊痰发热', '水湿', '虚积', '肝病惊风'], answer: [0], explain: '程氏脾虚条下谓"鱼骨形则水湿"，两说并存——主病以《证治准绳》为本、程氏用法互参。', source: '手纹十八图式' },
  { id: 'tp08', category: T, type: 'single', question: '水字形（三脉并行）主：', options: ['惊风、食积', '感冒寒邪', '饮食所伤', '肝木克脾败证'], answer: [0], explain: '水字形三脉并行。', source: '手纹十八图式' },
  { id: 'tp09', category: T, type: 'single', question: '针形（长针过命关一二粒米许）主：', options: ['心肝热极生风', '脾虚停食', '痰热', '寒邪'], answer: [0], explain: '长针形过命关一二粒米许。', source: '手纹十八图式' },
  { id: 'tp10', category: T, type: 'single', question: '透关射指形（命脉向里）主：', options: ['惊风、痰热聚于胸膈', '肝木克脾土之败证', '感冒寒邪', '饮食停滞'], answer: [0], explain: '向里为射指、向外为射甲。', source: '手纹十八图式' },
  { id: 'tp11', category: T, type: 'single', question: '透关射甲形（命脉向外）主：', options: ['惊风、肝木克脾土之败证', '风热', '食积', '虚寒'], answer: [0], explain: '射甲为败证，最重。', source: '手纹十八图式' },
  { id: 'tp12', category: T, type: 'single', question: '人字纹（即开长丫）主：', options: ['食、积', '惊', '风', '寒'], answer: [0], explain: '原著诊手纹法：开长丫为食、为积。', source: '诊手纹法' },
  { id: 'tp13', category: T, type: 'single', question: '短丫纹主：', options: ['惊', '食积', '湿热', '虚寒'], answer: [0], explain: '原著：短丫为惊。', source: '诊手纹法' },
  { id: 'tp14', category: T, type: 'single', question: '乱纹形主：', options: ['虚积（疳症条）', '风热', '痰热', '寒邪'], answer: [0], explain: '原著疳症条：乱纹为虚积。', source: '疳症诠治' },
  { id: 'tp15', category: T, type: 'single', question: '大小字形主：', options: ['肝病、惊风（依《四诊抉微》乙字形）', '食积', '虚寒', '湿热'], answer: [0], explain: '原著图注"大小字形"，《四诊抉微》乙字形主肝病惊风。', source: '手纹十八图式' },
  { id: 'tp16', category: T, type: 'single', question: '连珠形（此连珠之类）主：', options: ['危候（球形主死）', '脾虚', '风热', '食积'], answer: [0], explain: '《四诊抉微》：球形主死。', source: '手纹十八图式' },
  { id: 'tp17', category: T, type: 'single', question: '面部属位：额属何脏？', options: ['心（离火）', '肝（震木）', '脾（中土）', '肾（坎水）'], answer: [0], explain: '左腮属肝、右腮属肺、唇之上下属肾、鼻准属脾。', source: '小儿面部属位图' },
  { id: 'tp18', category: T, type: 'single', question: '面部五色：面黑而无润泽主：', options: ['肾气败', '热', '痛', '寒'], answer: [0], explain: '红病在心面红者热；青病在肝面青者痛；黄病在脾面黄者脾伤；白病在肺面白者寒。', source: '小儿面部属位图' },
  { id: 'tp19', category: T, type: 'single', question: '苗窍：舌为（　）之苗？', options: ['心', '肝', '脾', '肾'], answer: [0], explain: '舌乃心之苗：红紫心热、肿黑心火极、淡白虚。', source: '望形色审苗窍' },
  { id: 'tp20', category: T, type: 'single', question: '目部：白珠属肺，色青主：', options: ['肝风侮肺', '脾有积滞', '肺受湿热（疳症）', '肾气虚'], answer: [0], explain: '淡黄色脾有积滞；老黄色肺受湿热疳症。', source: '望形色审苗窍' },

  // ===== 危候 =====
  { id: 'wh01', category: W, type: 'single', question: '死症四十候中"肺绝"之候是：', options: ['鼻孔开张', '啼泣无声', '干呕无物', '唇牙枯白'], answer: [0], explain: '鼻孔开张、有出气无入气者为肺绝难治。', source: '死症四十候' },
  { id: 'wh02', category: W, type: 'single', question: '"唇牙枯白"属：', options: ['胃死', '脾绝', '肺绝', '肾绝'], answer: [0], explain: '胃死：唇牙枯白。', source: '死症四十候' },
  { id: 'wh03', category: W, type: 'single', question: '"舌黑如煤"属：', options: ['水克火', '热盛', '寒极', '瘀血'], answer: [0], explain: '水克火：舌黑如煤，死候。', source: '死症四十候' },
  { id: 'wh04', category: W, type: 'single', question: '"喉如拽锯"属：', options: ['骨绝', '肺绝', '肝绝', '血绝'], answer: [0], explain: '骨绝：喉如拽锯。', source: '死症四十候' },
  { id: 'wh05', category: W, type: 'single', question: '"发直如竖"属：', options: ['血绝', '气绝', '脾绝', '肾绝'], answer: [0], explain: '血绝：发直如竖。', source: '死症四十候' },
  { id: 'wh06', category: W, type: 'single', question: '"爪甲青黑"属：', options: ['肝血绝', '肺绝', '胃死', '肾绝'], answer: [0], explain: '肝血绝：爪甲青黑。', source: '死症四十候' },
  { id: 'wh07', category: W, type: 'single', question: '"肛门如筒"属：', options: ['气下绝', '脾绝', '脱液', '骨绝'], answer: [0], explain: '气下绝：肛门如筒。', source: '死症四十候' },
  { id: 'wh08', category: W, type: 'single', question: '"阴囊束缩"属：', options: ['肝肾绝', '脾绝', '肺绝', '血绝'], answer: [0], explain: '肝肾绝：阴囊束缩（原著"天囊束缩"）。', source: '死症四十候' },
  { id: 'wh09', category: W, type: 'single', question: '识症趋避："上而气喘、下而泄泻不止"之治：', options: ['难治，然亦以止泻为先', '先平喘', '先补气', '不可治'], answer: [0], explain: '下气定喘则泄泻愈甚、闭气止泻则喘愈甚，两下相碍，然以止泻为先。', source: '识症趋避' },
  { id: 'wh10', category: W, type: 'single', question: '识症趋避："病是症而服是症之药剂，愈剂愈剧者"：', options: ['必不祥', '药力不足', '剂量过大', '应加倍'], answer: [0], explain: '此为缓急相左。', source: '识症趋避' },
  { id: 'wh11', category: W, type: 'single', question: '遇死症难治，程氏的告诫是：', options: ['必先告明、令多请高明；须尽自己所学而救之、存济世心、勿计钱财', '推辞不治', '只求脱身', '照常开方不言语'], answer: [0], explain: '切勿见危而不救；勿苟且应酬、勿轻言不妨以图侥幸。', source: '识症趋避' },
  { id: 'wh12', category: W, type: 'single', question: '痢症坏候："色如屋上尘者"属：', options: ['黄变深，逆', '红变深，逆', '白变深，逆', '顺证'], answer: [0], explain: '黑如泥者红变深；鱼脑者白变深；屋尘者黄变深。', source: '痢症坏候' },

  // ===== 训诫推拿 =====
  { id: 'xj01', category: X, type: 'single', question: '九恨之"七恨"批评的是：', options: ['不问寒热，牛黄竹沥贝母概投儿服', '挑筋割肉', '丸散渔利', '内减外加'], answer: [0], explain: '热痰见此如滚汤泼雪、寒痰见此雪上加霜。', source: '九恨' },
  { id: 'xj02', category: X, type: 'single', question: '九恨之"八恨"批评的是：', options: ['脾虚肾虚、气血两虚之烧热亦用柴胡', '不用柴胡', '柴胡用量过大', '柴胡后下'], answer: [0], explain: '柴胡专属解表之味。', source: '九恨' },
  { id: 'xj03', category: X, type: 'single', question: '十三不可学中"鲁莽之人"的问题：', options: ['必不思索', '必无定见', '必不融通', '必多忽略'], answer: [0], explain: '犹豫之人必无定见；固执之人必不融通；轻浮之人必多忽略。', source: '十三不可学' },
  { id: 'xj04', category: X, type: 'single', question: '十传之"五传"：儿慢症的正确治法：', options: ['体贴"慢"字，不作惊治，唯补脾虚', '大剂镇惊', '重灸灯火', '攻下'], answer: [0], explain: '乱推乱拿乱掐乱火，以致汗愈亡阳、痛愈伤脾。', source: '十传' },
  { id: 'xj05', category: X, type: 'single', question: '十传之"九传"（把定舵牙）告诫：', options: ['望色真、辨窍确、药证合，病未除亦不可半路更方', '频频换方', '加大剂量', '改用丸散'], answer: [0], explain: '病深药浅、药力未到，如舟人把定舵牙，一任浪涌，自然到岸。', source: '十传' },
  { id: 'xj06', category: X, type: 'single', question: '推拿代药：推上三关代：', options: ['麻黄、肉桂', '滑石、羚羊', '黄连、犀角', '人参、白术'], answer: [0], explain: '退下六腑替来滑石羚羊。', source: '推拿代药赋' },
  { id: 'xj07', category: X, type: 'single', question: '推拿代药：水底捞月代：', options: ['黄连、犀角', '麻黄、肉桂', '诃子、炮姜', '桑皮、桔梗'], answer: [0], explain: '天河引水还同芩柏连翘。', source: '推拿代药赋' },
  { id: 'xj08', category: X, type: 'single', question: '大指脾面旋推为补、直推至指甲为：', options: ['泻', '补', '和', '清'], answer: [0], explain: '曲者旋也，旋推为补、直推至指甲为泻。', source: '掌面图说' },
  { id: 'xj09', category: X, type: 'single', question: '推三关、退六腑、运八卦的取手原则：', options: ['男女俱在左手', '男左女右', '男右女左', '两手皆可'], answer: [0], explain: '右掌无八卦；心肝诸脉俱在左手。', source: '掌面图说' },
  { id: 'xj10', category: X, type: 'single', question: '脐风灯火法：', options: ['灯火十三灼（三朝七日眼边黄即是脐风）', '元宵火十五', '艾灸百会', '灸鬼眼'], answer: [0], explain: '急将灯火十三点，此是医门第一方。', source: '灯火灸法' },
  { id: 'xj11', category: X, type: 'single', question: '定惊之火：', options: ['元宵火十五', '灯火十三灼', '艾灸肺俞', '灸龟尾'], answer: [0], explain: '疗惊定要元宵火，非火何能定得惊。', source: '灯火灸法' },
  { id: 'xj12', category: X, type: 'single', question: '推拿之时宜：', options: ['须下午，切莫在清晨', '清晨最佳', '午时', '夜半'], answer: [0], explain: '若用推拿须下午，推拿切莫在清晨。', source: '手法歌诀' },
  { id: 'xj13', category: X, type: 'single', question: '凡症初起用药原则（幼科铁镜凡例）：', options: ['不用丸散，因加减不便', '必用丸散', '只用推拿', '峻下'], answer: [0], explain: '药味分两已定，有一二味与症不宜者抽不出来。', source: '幼科铁镜凡例' },
  { id: 'xj14', category: X, type: 'single', question: '推三关与推六腑的配合：', options: ['推三关必须少推六腑以应之，反之亦然，防补泻太过', '只用其一', '各推百次', '无此说'], answer: [0], explain: '凡症，推三关必须少推腑上以应之。', source: '幼科铁镜凡例' },
]

/** 错题本工具 */
export function loadWrongIds(): string[] {
  try {
    return JSON.parse(localStorage.getItem('erke_wrong_ids') ?? '[]')
  } catch {
    return []
  }
}
export function saveWrongIds(ids: string[]) {
  localStorage.setItem('erke_wrong_ids', JSON.stringify(ids))
}
export function loadStats(): Record<string, { done: number; right: number }> {
  try {
    return JSON.parse(localStorage.getItem('erke_quiz_stats') ?? '{}')
  } catch {
    return {}
  }
}
export function saveStats(stats: Record<string, { done: number; right: number }>) {
  localStorage.setItem('erke_quiz_stats', JSON.stringify(stats))
}

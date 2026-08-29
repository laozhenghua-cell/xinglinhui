/**
 * 辨证论治引擎 — 依程氏诊法四步（诊手纹→切脉→看外症→问诊）采集证据，
 * 按八症主证特征加权评分辨证，依六字立法处方，并执行危候拦截。
 * 确定性规则引擎，所有结论均附原著依据。
 */
import { syndromes } from '../data/syndromes'
import { deathSigns, shizhengQubi, manpiJuehou } from '../data/deathSigns'

/** 四诊证据项定义 */
export interface FindingDef {
  key: string
  label: string
  step: 'shouwen' | 'mai' | 'wai' | 'wen'
  group: string
  hint?: string
}

export const findingGroups: { step: string; name: string; groups: { name: string; findings: FindingDef[] }[] }[] = [
  {
    step: 'shouwen',
    name: '一、望手纹（诊指纹）',
    groups: [
      {
        name: '浮沉（表里）',
        findings: [
          { key: 'w_fu', label: '纹浮（浮露于表）', step: 'shouwen', group: '浮沉', hint: '浮为风、为病在表' },
          { key: 'w_chen', label: '纹沉（隐于肉里）', step: 'shouwen', group: '浮沉', hint: '沉为里' },
          { key: 'w_yinxian', label: '纹或隐或现、或有或无', step: 'shouwen', group: '浮沉', hint: '慢脾风候，五脏气息已乱' },
        ],
      },
      {
        name: '颜色（风热寒虚）',
        findings: [
          { key: 'w_zi', label: '纹紫', step: 'shouwen', group: '颜色', hint: '紫为热' },
          { key: 'w_qing', label: '纹青', step: 'shouwen', group: '颜色', hint: '青为风' },
          { key: 'w_danhong', label: '纹淡红', step: 'shouwen', group: '颜色', hint: '淡红为寒' },
          { key: 'w_danzhi', label: '纹淡滞', step: 'shouwen', group: '颜色', hint: '淡滞为虚' },
          { key: 'w_mohu', label: '纹模糊不现', step: 'shouwen', group: '颜色', hint: '模糊不现为虚湿' },
          { key: 'w_cudazi', label: '纹粗大而紫', step: 'shouwen', group: '颜色', hint: '热盛浮现' },
          { key: 'w_yijie', label: '纹见一截一截模糊', step: 'shouwen', group: '颜色', hint: '伏热（阳症似阴）' },
        ],
      },
      {
        name: '纹形（十八图式）',
        findings: [
          { key: 'w_changya', label: '开长丫（人字纹）', step: 'shouwen', group: '纹形', hint: '为食、为积' },
          { key: 'w_duanya', label: '开短丫', step: 'shouwen', group: '纹形', hint: '为惊' },
          { key: 'w_gongfanwai', label: '弓反外形', step: 'shouwen', group: '纹形', hint: '痰热；慢惊见之者重' },
          { key: 'w_gongfanli', label: '弓反内形', step: 'shouwen', group: '纹形', hint: '感冒寒邪' },
          { key: 'w_shuizi', label: '水字形', step: 'shouwen', group: '纹形', hint: '惊风、食积' },
          { key: 'w_yugu', label: '鱼骨形', step: 'shouwen', group: '纹形', hint: '水湿' },
          { key: 'w_liuzhu', label: '流珠形', step: 'shouwen', group: '纹形', hint: '饮食所伤、内热' },
          { key: 'w_huanzhu', label: '环珠形', step: 'shouwen', group: '纹形', hint: '脾虚停食' },
          { key: 'w_changzhu', label: '长珠形', step: 'shouwen', group: '纹形', hint: '脾伤积滞' },
          { key: 'w_laishe', label: '来蛇形', step: 'shouwen', group: '纹形', hint: '脾胃湿热' },
          { key: 'w_qushe', label: '去蛇形', step: 'shouwen', group: '纹形', hint: '脾虚食积' },
          { key: 'w_qiang', label: '枪形', step: 'shouwen', group: '纹形', hint: '风热' },
          { key: 'w_zhen', label: '针形（透命关）', step: 'shouwen', group: '纹形', hint: '心肝热极生风' },
          { key: 'w_shezhi', label: '透关射指形', step: 'shouwen', group: '纹形', hint: '惊风、痰热聚胸膈' },
          { key: 'w_shejia', label: '透关射甲形', step: 'shouwen', group: '纹形', hint: '肝木克脾土败证' },
          { key: 'w_luanwen', label: '乱纹（参差离乱）', step: 'shouwen', group: '纹形', hint: '虚积；慢惊右手离乱' },
          { key: 'w_daxiaoz', label: '大小字形', step: 'shouwen', group: '纹形', hint: '肝病、惊风' },
          { key: 'w_lianzhu', label: '连珠形', step: 'shouwen', group: '纹形', hint: '危候' },
          { key: 'w_sandamaosheng', label: '纹散大生毛', step: 'shouwen', group: '纹形', hint: '虚湿' },
          { key: 'w_sanwutiao', label: '纹三五条不等', step: 'shouwen', group: '纹形', hint: '热积（急惊夹惊）' },
        ],
      },
      {
        name: '关位与左右',
        findings: [
          { key: 'w_fengguan', label: '纹在风关', step: 'shouwen', group: '关位与左右', hint: '病初起，症轻' },
          { key: 'w_qiguan', label: '纹至气关', step: 'shouwen', group: '关位与左右', hint: '病进' },
          { key: 'w_mingguan', label: '纹出命关', step: 'shouwen', group: '关位与左右', hint: '病甚；慢脾久病见之为危候' },
          { key: 'w_zuofu', label: '左手纹浮于右手', step: 'shouwen', group: '关位与左右', hint: '肝经风热（左手主肝）' },
          { key: 'w_youfu', label: '右手纹浮于左手', step: 'shouwen', group: '关位与左右', hint: '肺经（右手主肺），咳嗽必见' },
        ],
      },
    ],
  },
  {
    step: 'mai',
    name: '二、切脉',
    groups: [
      {
        name: '脉象',
        findings: [
          { key: 'm_fu', label: '脉浮', step: 'mai', group: '脉象', hint: '浮为风、为表' },
          { key: 'm_chen', label: '脉沉', step: 'mai', group: '脉象', hint: '沉为里' },
          { key: 'm_shu', label: '脉数（一息八九至以上）', step: 'mai', group: '脉象', hint: '数为热' },
          { key: 'm_chi', label: '脉迟', step: 'mai', group: '脉象', hint: '迟为寒' },
          { key: 'm_hua', label: '脉滑', step: 'mai', group: '脉象', hint: '滑为痰' },
          { key: 'm_xian', label: '脉弦', step: 'mai', group: '脉象', hint: '弦主肝、疟' },
          { key: 'm_jin', label: '脉紧', step: 'mai', group: '脉象', hint: '紧为寒' },
          { key: 'm_ru', label: '脉濡', step: 'mai', group: '脉象', hint: '濡主脾虚湿' },
        ],
      },
      {
        name: '虚实与左右',
        findings: [
          { key: 'm_youli', label: '脉有力', step: 'mai', group: '虚实与左右', hint: '有力为实' },
          { key: 'm_wuli', label: '脉无力', step: 'mai', group: '虚实与左右', hint: '无力为虚' },
          { key: 'm_sanluan', label: '脉浮泛无力、脉息离乱、十余至重按则无（散脉）', step: 'mai', group: '虚实与左右', hint: '慢脾风散脉，难望有生' },
          { key: 'm_weixu', label: '脉微而不乱、重按迟而有力', step: 'mai', group: '虚实与左右', hint: '元气尚藏，有望' },
          { key: 'm_zuoshen', label: '左手脉甚于右手', step: 'mai', group: '虚实与左右', hint: '肝木乘土；燥火为重' },
          { key: 'm_youshen', label: '右手脉甚于左手', step: 'mai', group: '虚实与左右', hint: '燥火为轻' },
          { key: 'm_buqi', label: '脉迟数大小参差不齐', step: 'mai', group: '虚实与左右', hint: '内有积滞' },
        ],
      },
    ],
  },
  {
    step: 'wai',
    name: '三、看外症（望诊）',
    groups: [
      {
        name: '神色与热象',
        findings: [
          { key: 'g_shenre', label: '身热', step: 'wai', group: '神色与热象' },
          { key: 'g_zhuangre', label: '壮热（日夜俱热）', step: 'wai', group: '神色与热象' },
          { key: 'g_yerre', label: '夜间热增', step: 'wai', group: '神色与热象', hint: '火伏于内' },
          { key: 'g_riqingyezhong', label: '日轻夜重', step: 'wai', group: '神色与热象', hint: '虚热内热' },
          { key: 'g_chaore', label: '潮热（定时而作）', step: 'wai', group: '神色与热象', hint: '虚热' },
          { key: 'g_hanre', label: '寒热往来', step: 'wai', group: '神色与热象', hint: '热在少阳' },
          { key: 'g_xianleng', label: '先冷后热（定时发作）', step: 'wai', group: '神色与热象', hint: '疟疾' },
          { key: 'g_mianhong', label: '面目红赤', step: 'wai', group: '神色与热象' },
          { key: 'g_mianhuangbai', label: '面色黄白', step: 'wai', group: '神色与热象' },
          { key: 'g_mianhuangshou', label: '面黄肌瘦', step: 'wai', group: '神色与热象' },
          { key: 'g_mianqing', label: '面青', step: 'wai', group: '神色与热象' },
          { key: 'g_mianhei', label: '面黑', step: 'wai', group: '神色与热象' },
          { key: 'g_shenjuan', label: '神倦无精神、倦怠依人', step: 'wai', group: '神色与热象' },
          { key: 'g_bimuwanghun', label: '闭目亡魂', step: 'wai', group: '神色与热象', hint: '风闭五脏（慢脾危候）' },
          { key: 'g_shenhunmubi', label: '神昏目闭、形如醉人、唤之则醒', step: 'wai', group: '神色与热象', hint: '伏热内闭' },
          { key: 'g_zhanyu', label: '时发谵语', step: 'wai', group: '神色与热象', hint: '心伏火' },
        ],
      },
      {
        name: '头面苗窍（唇鼻眼舌耳发）',
        findings: [
          { key: 'g_chunshenhong', label: '唇深红而亮', step: 'wai', group: '头面苗窍', hint: '风热' },
          { key: 'g_chunjiaoan', label: '唇红而焦暗', step: 'wai', group: '头面苗窍', hint: '实热' },
          { key: 'g_chundanbai', label: '唇淡白', step: 'wai', group: '头面苗窍', hint: '脾胃虚寒' },
          { key: 'g_chundanhuang', label: '唇黄淡暗', step: 'wai', group: '头面苗窍', hint: '湿热' },
          { key: 'g_chunkubai', label: '唇枯白如朽骨', step: 'wai', group: '头面苗窍', hint: '脾绝死症' },
          { key: 'g_bisai', label: '鼻塞、流涕水', step: 'wai', group: '头面苗窍', hint: '风热在肺' },
          { key: 'g_bigan', label: '鼻干、鼻燥', step: 'wai', group: '头面苗窍', hint: '燥热伤津' },
          { key: 'g_bikongkaizhang', label: '鼻孔开张、有出气无入气', step: 'wai', group: '头面苗窍', hint: '肺绝难治' },
          { key: 'g_biheimei', label: '鼻生黑煤（洗而忽然）', step: 'wai', group: '头面苗窍', hint: '难治（识症趋避）' },
          { key: 'g_yanqinglei', label: '眼有清泪', step: 'wai', group: '头面苗窍', hint: '风、虚' },
          { key: 'g_yanleijiang', label: '眼有泪浆黄结', step: 'wai', group: '头面苗窍', hint: '风、湿、热' },
          { key: 'g_yanshishi', label: '眼直视或上视', step: 'wai', group: '头面苗窍', hint: '肝风发搐' },
          { key: 'g_yanbaiqinglan', label: '眼白青蓝色', step: 'wai', group: '头面苗窍', hint: '肝有风' },
          { key: 'g_tongwuguang', label: '瞳无光彩', step: 'wai', group: '头面苗窍', hint: '肾虚；兼发黄肾气虚' },
          { key: 'g_yanbaihuang', label: '眼白黄', step: 'wai', group: '头面苗窍', hint: '湿热' },
          { key: 'g_yanshihuangjie', label: '眼屎黄结', step: 'wai', group: '头面苗窍', hint: '内热' },
          { key: 'g_yankuangxian', label: '眼眶微陷／深陷', step: 'wai', group: '头面苗窍', hint: '脾气不升；深陷者危' },
          { key: 'g_shebaitai', label: '舌白苔', step: 'wai', group: '头面苗窍', hint: '风' },
          { key: 'g_shehuanggan', label: '苔黄而干', step: 'wai', group: '头面苗窍', hint: '热' },
          { key: 'g_shehong', label: '舌红', step: 'wai', group: '头面苗窍', hint: '心火' },
          { key: 'g_shehei', label: '舌黑苔而干', step: 'wai', group: '头面苗窍', hint: '热盛' },
          { key: 'g_sheheiMei', label: '舌黑如煤', step: 'wai', group: '头面苗窍', hint: '水克火，死候' },
          { key: 'g_ebeiwen', label: '耳背有纹（乱纹）', step: 'wai', group: '头面苗窍', hint: '防出痘疹，乱纹为凶' },
          { key: 'g_faxihuang', label: '头发稀疏带黄', step: 'wai', group: '头面苗窍', hint: '虚弱' },
          { key: 'g_fasui', label: '头毛生穗（疏密长短不等）', step: 'wai', group: '头面苗窍', hint: '有积病' },
          { key: 'g_fashu', label: '发竖向上（直指向天）', step: 'wai', group: '头面苗窍', hint: '乳母有胎（喜病）；无故如此为急死之症' },
          { key: 'g_fazhi', label: '发直如竖', step: 'wai', group: '头面苗窍', hint: '血绝，死候' },
        ],
      },
      {
        name: '肢体与躯干',
        findings: [
          { key: 'g_shouzuleng', label: '手足冷（无温）', step: 'wai', group: '肢体与躯干', hint: '脾受克；常冷无温为脾气欲绝' },
          { key: 'g_fajue', label: '发厥（四肢冷不知人事）', step: 'wai', group: '肢体与躯干', hint: '厥为风重' },
          { key: 'g_chouchi', label: '抽掣（筋络抽动）', step: 'wai', group: '肢体与躯干', hint: '肝风' },
          { key: 'g_woquan', label: '两手握拳', step: 'wai', group: '肢体与躯干', hint: '惊' },
          { key: 'g_yaoya', label: '咬牙', step: 'wai', group: '肢体与躯干', hint: '肝风' },
          { key: 'g_shuizhongjingti', label: '睡中惊惕、手足常惕', step: 'wai', group: '肢体与躯干', hint: '心惊' },
          { key: 'g_duqingjin', label: '肚大青筋', step: 'wai', group: '肢体与躯干', hint: '疳积' },
          { key: 'g_qizhangrugu', label: '肚皮胀薄、青筋绕露、气胀如鼓', step: 'wai', group: '肢体与躯干', hint: '气郁有积' },
          { key: 'g_shennang', label: '肾囊软大长垂／光亮如水', step: 'wai', group: '肢体与躯干', hint: '儿弱；膀胱气弱停水' },
          { key: 'g_shuizhong', label: '水肿', step: 'wai', group: '肢体与躯干', hint: '脾虚受湿' },
        ],
      },
      {
        name: '咳喘痰涎',
        findings: [
          { key: 'g_kesou', label: '咳嗽（有痰有声）', step: 'wai', group: '咳喘痰涎' },
          { key: 'g_ganke', label: '干咳无痰', step: 'wai', group: '咳喘痰涎', hint: '燥火烁肺' },
          { key: 'g_keshengzhong', label: '咳声似重、连咳数声而痰始出', step: 'wai', group: '咳喘痰涎', hint: '风痰闭肺' },
          { key: 'g_tishui', label: '涕水淋漓、眼有泪浆（咳嗽）', step: 'wai', group: '咳喘痰涎', hint: '风热之咳' },
          { key: 'g_tanming', label: '喉中痰鸣如锯', step: 'wai', group: '咳喘痰涎', hint: '风痰壅喉（急惊）' },
          { key: 'g_qichuan', label: '气喘', step: 'wai', group: '咳喘痰涎' },
          { key: 'g_yezhongchenqing', label: '夜间喘热惊惕、晨则平复（吼症）', step: 'wai', group: '咳喘痰涎', hint: '乳痰吼症' },
          { key: 'g_shiyin', label: '声音不亮、甚则失音', step: 'wai', group: '咳喘痰涎', hint: '燥火伤肺' },
        ],
      },
      {
        name: '汗与啼哭',
        findings: [
          { key: 'g_zihan', label: '自汗（醒时无故出汗）', step: 'wai', group: '汗与啼哭', hint: '脾虚腠理不固' },
          { key: 'g_daohan', label: '盗汗（睡中出汗）', step: 'wai', group: '汗与啼哭', hint: '气不归藏' },
          { key: 'g_lengan', label: '汗出而滑、身冷气长吁', step: 'wai', group: '汗与啼哭', hint: '慢脾无望之候' },
          { key: 'g_tiku', label: '啼哭无声', step: 'wai', group: '汗与啼哭', hint: '气绝，死候' },
          { key: 'g_xikulianmu', label: '善啼、恋母', step: 'wai', group: '汗与啼哭' },
        ],
      },
    ],
  },
  {
    step: 'wen',
    name: '四、问诊',
    groups: [
      {
        name: '二便',
        findings: [
          { key: 'q_xieqinghuang', label: '泻青黄色、有水有渣如浮萍', step: 'wen', group: '二便', hint: '风热' },
          { key: 'q_xiehuangshui', label: '泻净黄水', step: 'wen', group: '二便', hint: '湿热、内热' },
          { key: 'q_xiebaishui', label: '泻净白水（白屎汤）', step: 'wen', group: '二便', hint: '脾胃虚寒' },
          { key: 'q_xiebaihu', label: '泻白如糊状而酸臭', step: 'wen', group: '二便', hint: '伤食' },
          { key: 'q_xiebaimo', label: '泻白沫', step: 'wen', group: '二便', hint: '气分湿热' },
          { key: 'q_xiehongmo', label: '泻红沫', step: 'wen', group: '二便', hint: '血分湿热' },
          { key: 'q_xiehuangmo', label: '泻黄沫', step: 'wen', group: '二便', hint: '脾经湿热' },
          { key: 'q_xieqingxue', label: '泻清血', step: 'wen', group: '二便', hint: '血分' },
          { key: 'q_xieheishui', label: '频泻黑水', step: 'wen', group: '二便', hint: '死候' },
          { key: 'q_liji', label: '下痢（红白黄相兼）', step: 'wen', group: '二便', hint: '痢症' },
          { key: 'q_xiaoduanshu', label: '小便短黄', step: 'wen', group: '二便', hint: '有热、有湿火' },
          { key: 'q_xiaochangbai', label: '小便长白', step: 'wen', group: '二便', hint: '无热' },
          { key: 'q_baijiang', label: '小便落地结白浆', step: 'wen', group: '二便', hint: '大湿热' },
          { key: 'q_bianbi', label: '大便闭结不通', step: 'wen', group: '二便', hint: '热闭' },
        ],
      },
      {
        name: '渴饮与吐',
        findings: [
          { key: 'q_keyinleng', label: '渴而饮冷', step: 'wen', group: '渴饮与吐', hint: '内湿热' },
          { key: 'q_keyinre', label: '渴而饮热', step: 'wen', group: '渴饮与吐', hint: '内热、风热传里' },
          { key: 'q_dake', label: '大渴引饮', step: 'wen', group: '渴饮与吐', hint: '热盛伤津' },
          { key: 'q_outu', label: '呕吐', step: 'wen', group: '渴饮与吐' },
          { key: 'q_ouru', label: '食入即吐', step: 'wen', group: '渴饮与吐', hint: '胃火内冲' },
          { key: 'q_ganou', label: '干呕无物', step: 'wen', group: '渴饮与吐', hint: '胃气绝，死候' },
        ],
      },
      {
        name: '饮食与兼夹',
        findings: [
          { key: 'q_shangshi', label: '伤食（有饮食不节之因）', step: 'wen', group: '饮食与兼夹' },
          { key: 'q_shibuzhibao', label: '食不知饱、愈食愈瘦', step: 'wen', group: '饮食与兼夹', hint: '疳积' },
          { key: 'q_shihouxie', label: '食后即泻', step: 'wen', group: '饮食与兼夹', hint: '脾不运化' },
          { key: 'q_buyinshi', label: '不饮食', step: 'wen', group: '饮食与兼夹' },
          { key: 'q_youjou', label: '有痰', step: 'wen', group: '饮食与兼夹' },
          { key: 'q_jiashu', label: '夹暑（暑月发病）', step: 'wen', group: '饮食与兼夹' },
          { key: 'q_jiashi', label: '夹湿', step: 'wen', group: '饮食与兼夹' },
          { key: 'q_duanru', label: '失乳（断乳后得病）', step: 'wen', group: '饮食与兼夹' },
          { key: 'q_rumuyoutai', label: '乳母有胎（儿食孕乳）', step: 'wen', group: '饮食与兼夹' },
        ],
      },
      {
        name: '惊搐征象',
        findings: [
          { key: 'q_shuizhongtiao', label: '夜间睡着手足跳动', step: 'wen', group: '惊搐征象', hint: '有惊' },
          { key: 'q_jijingbingshi', label: '有急惊病史、失治迁延', step: 'wen', group: '惊搐征象', hint: '传慢惊之由' },
          { key: 'q_buyu', label: '不语', step: 'wen', group: '惊搐征象', hint: '脾气将绝' },
          { key: 'q_tuxiebuZhi', label: '吐泻不止（吐泻兼作）', step: 'wen', group: '惊搐征象', hint: '慢惊最危之候' },
        ],
      },
    ],
  },
]

/** 所有证据项 flat 索引 */
export const findingIndex: Record<string, FindingDef> = {}
for (const step of findingGroups)
  for (const grp of step.groups) for (const f of grp.findings) findingIndex[f.key] = f

/**
 * 八症辨证规则：命中证据的加权得分。
 * 权重 3 = 主证（诊断性），2 = 常见，1 = 参考。
 */
export interface SyndromeRule {
  id: string
  features: { key: string; w: number }[]
}

export const syndromeRules: SyndromeRule[] = [
  {
    id: 'fengre',
    features: [
      { key: 'w_fu', w: 3 }, { key: 'w_zi', w: 3 }, { key: 'w_zuofu', w: 2 },
      { key: 'm_fu', w: 2 }, { key: 'm_shu', w: 2 }, { key: 'm_zuoshen', w: 1 },
      { key: 'g_chunshenhong', w: 3 }, { key: 'g_shenre', w: 2 }, { key: 'g_bisai', w: 2 },
      { key: 'q_xieqinghuang', w: 3 }, { key: 'g_zhuangre', w: 2 },
    ],
  },
  {
    id: 'jijing',
    features: [
      { key: 'g_shuizhongjingti', w: 3 }, { key: 'g_chouchi', w: 3 },
      { key: 'g_yanshishi', w: 3 }, { key: 'g_yaoya', w: 2 }, { key: 'g_tanming', w: 3 },
      { key: 'w_duanya', w: 2 }, { key: 'w_sanwutiao', w: 2 }, { key: 'w_fu', w: 1 },
      { key: 'm_fu', w: 1 }, { key: 'm_hua', w: 2 }, { key: 'm_shu', w: 1 },
      { key: 'g_woquan', w: 2 }, { key: 'g_chunshenhong', w: 1 }, { key: 'g_shenre', w: 1 },
      { key: 'w_zuofu', w: 1 }, { key: 'q_shuizhongtiao', w: 2 },
    ],
  },
  {
    id: 'manjing',
    features: [
      { key: 'q_jijingbingshi', w: 3 }, { key: 'g_shouzuleng', w: 3 }, { key: 'g_fajue', w: 2 },
      { key: 'q_tuxiebuZhi', w: 3 }, { key: 'w_chen', w: 2 }, { key: 'w_qing', w: 3 },
      { key: 'm_chen', w: 2 }, { key: 'm_chi', w: 2 }, { key: 'm_wuli', w: 1 },
      { key: 'm_jin', w: 1 }, { key: 'g_chundanbai', w: 2 }, { key: 'g_yankuangxian', w: 2 },
      { key: 'g_yanbaiqinglan', w: 2 }, { key: 'q_xiebaishui', w: 2 }, { key: 'q_xiehuangshui', w: 2 },
      { key: 'w_gongfanwai', w: 2 }, { key: 'w_gongfanli', w: 2 }, { key: 'w_changya', w: 2 },
      { key: 'w_luanwen', w: 2 }, { key: 'q_outu', w: 2 }, { key: 'g_qichuan', w: 1 },
    ],
  },
  {
    id: 'manpi',
    features: [
      { key: 'q_xiebaishui', w: 3 }, { key: 'g_shouzuleng', w: 3 }, { key: 'g_bimuwanghun', w: 3 },
      { key: 'g_chundanbai', w: 3 }, { key: 'q_buyinshi', w: 2 }, { key: 'q_buyu', w: 2 },
      { key: 'w_yinxian', w: 2 }, { key: 'm_sanluan', w: 3 }, { key: 'g_lengan', w: 3 },
      { key: 'q_outu', w: 2 }, { key: 'q_tuxiebuZhi', w: 2 }, { key: 'm_wuli', w: 1 },
      { key: 'm_weixu', w: 2 },
    ],
  },
  {
    id: 'pixu',
    features: [
      { key: 'g_mianhuangbai', w: 3 }, { key: 'g_shenjuan', w: 2 }, { key: 'g_chundanbai', w: 2 },
      { key: 'g_faxihuang', w: 2 }, { key: 'g_xikulianmu', w: 1 }, { key: 'g_chaore', w: 2 },
      { key: 'g_riqingyezhong', w: 2 }, { key: 'g_daohan', w: 2 }, { key: 'g_zihan', w: 2 },
      { key: 'w_danhong', w: 2 }, { key: 'w_danzhi', w: 2 }, { key: 'w_sandamaosheng', w: 2 },
      { key: 'w_qiguan', w: 2 }, { key: 'w_mingguan', w: 2 }, { key: 'w_changya', w: 1 },
      { key: 'w_yugu', w: 1 }, { key: 'm_ru', w: 2 }, { key: 'm_wuli', w: 2 },
      { key: 'm_zuoshen', w: 2 }, { key: 'q_shangshi', w: 1 }, { key: 'g_shuizhong', w: 2 },
      { key: 'q_duanru', w: 2 },
    ],
  },
  {
    id: 'ganji',
    features: [
      { key: 'g_mianhuangshou', w: 3 }, { key: 'g_fasui', w: 3 }, { key: 'g_duqingjin', w: 3 },
      { key: 'q_shibuzhibao', w: 2 }, { key: 'q_shihouxie', w: 2 }, { key: 'w_luanwen', w: 2 },
      { key: 'w_changya', w: 2 }, { key: 'm_xian', w: 2 }, { key: 'm_buqi', w: 2 },
      { key: 'g_qizhangrugu', w: 2 }, { key: 'm_chen', w: 1 }, { key: 'g_yerre', w: 1 },
      { key: 'q_buyinshi', w: 1 }, { key: 'g_mianhuangbai', w: 1 },
    ],
  },
  {
    id: 'zaohuo',
    features: [
      { key: 'g_mianhong', w: 3 }, { key: 'g_chunshenhong', w: 2 }, { key: 'g_koubiganzao', w: 3 },
      { key: 'q_dake', w: 3 }, { key: 'g_yerre', w: 3 }, { key: 'g_zhanyu', w: 2 },
      { key: 'g_hanre', w: 2 }, { key: 'g_yanshihuangjie', w: 2 }, { key: 'q_xiaoduanshu', w: 2 },
      { key: 'q_ouru', w: 1 }, { key: 'g_shenhunmubi', w: 1 }, { key: 'w_cudazi', w: 3 },
      { key: 'w_yijie', w: 2 }, { key: 'm_hua', w: 2 }, { key: 'm_shu', w: 2 }, { key: 'm_youli', w: 2 },
      { key: 'q_bianbi', w: 2 }, { key: 'g_zhuangre', w: 1 }, { key: 'g_ganke', w: 1 },
    ],
  },
  {
    id: 'kesou',
    features: [
      { key: 'g_kesou', w: 3 }, { key: 'g_ganke', w: 2 }, { key: 'w_youfu', w: 3 },
      { key: 'w_fu', w: 1 }, { key: 'w_zi', w: 1 }, { key: 'w_chen', w: 1 }, { key: 'w_zi', w: 1 },
      { key: 'w_duanya', w: 1 }, { key: 'w_changya', w: 1 }, { key: 'm_fu', w: 1 },
      { key: 'm_hua', w: 2 }, { key: 'g_keshengzhong', w: 2 }, { key: 'g_tishui', w: 2 },
      { key: 'g_yezhongchenqing', w: 2 }, { key: 'g_tanming', w: 1 }, { key: 'g_qichuan', w: 1 },
      { key: 'g_shiyin', w: 1 }, { key: 'g_bigan', w: 1 }, { key: 'g_zihan', w: 1 },
    ],
  },
]

/** 口鼻干燥证据（外症补充） */
;(() => {
  // 注册 g_koubiganzao（口鼻干燥）——在"头面苗窍"组中追加
  const wai = findingGroups.find((s) => s.step === 'wai')!
  const grp = wai.groups.find((g) => g.name.startsWith('头面苗窍'))!
  grp.findings.push({
    key: 'g_koubiganzao',
    label: '口鼻干燥',
    step: 'wai',
    group: '头面苗窍',
    hint: '内有火故干燥（燥火）',
  })
  findingIndex['g_koubiganzao'] = grp.findings[grp.findings.length - 1]
})()

/** 危候拦截规则：命中任一即触发危候警示 */
export const dangerRules: { key: string; label: string; level: '极危' | '危' }[] = [
  { key: 'g_tiku', label: '啼哭无声（气绝）', level: '极危' },
  { key: 'g_bikongkaizhang', label: '鼻孔开张（肺绝）', level: '极危' },
  { key: 'q_ganou', label: '干呕无物（胃气绝）', level: '极危' },
  { key: 'g_yankuangxian', label: '眼眶深陷（脾绝）', level: '极危' },
  { key: 'g_chunkubai', label: '唇枯白如朽骨（脾绝）', level: '极危' },
  { key: 'g_sheheiMei', label: '舌黑如煤（水克火）', level: '极危' },
  { key: 'g_fazhi', label: '发直如竖（血绝）', level: '极危' },
  { key: 'q_xieheishui', label: '频泻黑水（死候）', level: '极危' },
  { key: 'g_biheimei', label: '鼻生黑煤洗而忽然（难治）', level: '极危' },
  { key: 'g_lengan', label: '汗出而滑、身冷气长吁（慢脾无望）', level: '极危' },
  { key: 'm_sanluan', label: '脉息离乱、十余至重按则无（散脉）', level: '极危' },
  { key: 'g_bimuwanghun', label: '闭目亡魂（风闭五脏）', level: '极危' },
  { key: 'q_buyu', label: '不语（脾气将绝）', level: '极危' },
  { key: 'g_shouzuleng', label: '手足常冷无温（脾气欲绝）', level: '危' },
  { key: 'q_tuxiebuZhi', label: '吐泻不止（吐泻兼作，土绝）', level: '极危' },
  { key: 'g_qichuan', label: '气喘（须辨咳喘与胃气欲脱之喘）', level: '危' },
]

/** 组合危候：慢脾风危急组合 */
export const comboDangers = [
  {
    label: '慢脾风危急组合（呕吐、泄泻白屎汤不止 + 手足常冷 + 闭目亡魂 + 唇淡白 + 不食不语）',
    keys: ['q_outu', 'q_xiebaishui', 'g_shouzuleng', 'g_bimuwanghun', 'g_chundanbai'],
    min: 4,
  },
  {
    label: '上喘下泻两下相碍（难治，当以止泻为先）',
    keys: ['g_qichuan', 'q_tuxiebuZhi'],
    min: 2,
  },
]

/** 兼症→加减法映射（按八症条下加减法） */
export const jiajianMapping: { key: string; label: string; match: string[] }[] = [
  { key: 'q_shangshi', label: '伤食', match: ['伤食', '夹食', '食积'] },
  { key: 'q_youjou', label: '有痰', match: ['痰'] },
  { key: 'q_jiashu', label: '夹暑', match: ['暑'] },
  { key: 'q_jiashi', label: '夹湿', match: ['湿'] },
  { key: 'g_qichuan', label: '气喘', match: ['喘'] },
  { key: 'q_tuxiebuZhi', label: '吐泻不止', match: ['吐', '泻', '泄泻'] },
  { key: 'g_yerre', label: '夜间热增', match: ['热'] },
  { key: 'q_outu', label: '呕吐', match: ['呕', '吐'] },
  { key: 'g_zihan', label: '自汗', match: ['汗'] },
  { key: 'g_daohan', label: '盗汗', match: ['汗'] },
]

/** 辨证结果 */
export interface DiagnosisResult {
  scores: { id: string; name: string; score: number; pct: number }[]
  top: { id: string; name: string; pct: number }[]
  methods: string[]
  dangers: { label: string; level: '极危' | '危' }[]
  combos: string[]
  jiajianHits: { syndrome: string; cond: string; add: string; note?: string }[]
  selected: Record<string, boolean>
}

export function diagnose(selected: Record<string, boolean>): DiagnosisResult {
  const dangers: { label: string; level: '极危' | '危' }[] = []
  for (const d of dangerRules) if (selected[d.key]) dangers.push({ label: d.label, level: d.level })
  const combos: string[] = []
  for (const c of comboDangers) {
    const hit = c.keys.filter((k) => selected[k]).length
    if (hit >= c.min) combos.push(c.label)
  }

  const scores = syndromeRules.map((rule) => {
    let score = 0
    for (const f of rule.features) if (selected[f.key]) score += f.w
    return score
  })
  const max = Math.max(...scores, 1)
  const scored = syndromeRules
    .map((rule, i) => {
      const s = syndromes.find((x) => x.id === rule.id)!
      const pct = Math.round((scores[i] / max) * 100)
      return { id: rule.id, name: s.name, score: scores[i], pct }
    })
    .sort((a, b) => b.score - a.score)

  const top = scored.filter((s) => s.score > 0 && s.pct >= 45).slice(0, 2)

  // 治法六字合并
  const methods: string[] = []
  for (const t of top) {
    const s = syndromes.find((x) => x.id === t.id)!
    for (const m of s.methods) if (!methods.includes(m)) methods.push(m)
  }

  // 加减法匹配
  const jiajianHits: { syndrome: string; cond: string; add: string; note?: string }[] = []
  for (const t of top) {
    const s = syndromes.find((x) => x.id === t.id)!
    for (const j of s.jiajian) {
      const hit = jiajianMapping.some(
        (m) => selected[m.key] && m.match.some((w) => j.cond.includes(w))
      )
      if (hit) jiajianHits.push({ syndrome: s.name, cond: j.cond, add: j.add, note: j.note })
    }
  }

  return { scores: scored, top, methods, dangers, combos, jiajianHits, selected }
}

/** 危候总表（用于危候警示页展示原著死症四十候） */
export const deathSignList = deathSigns
export const qubiList = shizhengQubi
export const manpiJuehouText = manpiJuehou

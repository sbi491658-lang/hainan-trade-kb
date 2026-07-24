#!/usr/bin/env python3
"""
v5.2 — 多页面架构 · 视觉重塑 · AI助手 · 贸易工具 · 数据叙事
Flask + MySQL + ECharts
"""
import mysql.connector
from flask import Flask, jsonify, render_template_string, send_from_directory, request
import os, re

POSTER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posters")
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['DEFAULT_CHARSET'] = 'utf-8'

DB_CONFIG = {"host":"localhost","port":3306,"user": "root", "password": "Root@2026!","database":"hainan_ai_trade","charset":"utf8mb4"}
# Embedded data fallback (no MySQL needed)
_EMBEDDED = None
_EMBEDDED_MAP = {
    "timeline": "timeline", "risks": "risks", "tech_arch": "tech_arch",
    "scenarios": "scenarios", "articles": "articles"
}
def _load_embedded():
    global _EMBEDDED
    if _EMBEDDED is None:
        import json
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embedded_data.json")
        with open(path, "r", encoding="utf-8") as f:
            _EMBEDDED = json.load(f)
    return _EMBEDDED


def get_db(): return mysql.connector.connect(**DB_CONFIG)
def dict_cursor():
    conn=get_db(); return conn, conn.cursor(dictionary=True)

# ==================== DATABASE ====================
def init_db():
    conn=get_db(); cur=conn.cursor()
    for t in ["scenarios","key_metrics","local_cases","articles","risk_warnings",
              "policy_timeline","roadmap_phases","tech_architecture",
              "trade_routes","competitors","data_screen","business_steps"]:
        cur.execute(f"DROP TABLE IF EXISTS {t}")

    cur.execute("""CREATE TABLE scenarios (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), icon VARCHAR(20),
        pain_point TEXT, ai_solution TEXT, slogan VARCHAR(200), key_data TEXT,
        local_case TEXT, eff INT, tech INT, policy INT, sort_order INT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE key_metrics (id INT AUTO_INCREMENT PRIMARY KEY, metric_name VARCHAR(200),
        metric_value VARCHAR(100), source VARCHAR(200), category VARCHAR(50)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE local_cases (id INT AUTO_INCREMENT PRIMARY KEY, case_name VARCHAR(200),
        executor VARCHAR(200), location VARCHAR(100), tech TEXT, effect TEXT,
        source VARCHAR(200), scenario_id INT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE articles (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(200), summary TEXT,
        content LONGTEXT, article_type VARCHAR(50), created_at VARCHAR(50)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE risk_warnings (id INT AUTO_INCREMENT PRIMARY KEY, risk_type VARCHAR(100),
        risk_level VARCHAR(10), description TEXT, solution TEXT, hainan_measure TEXT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE policy_timeline (id INT AUTO_INCREMENT PRIMARY KEY, event_date VARCHAR(50),
        event_title VARCHAR(200), event_desc TEXT, category VARCHAR(50)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE roadmap_phases (id INT AUTO_INCREMENT PRIMARY KEY, phase_name VARCHAR(100),
        phase_time VARCHAR(50), objectives TEXT, key_tasks TEXT, status VARCHAR(20)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE tech_architecture (id INT AUTO_INCREMENT PRIMARY KEY, layer_name VARCHAR(100),
        layer_order INT, components TEXT, description TEXT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE trade_routes (id INT AUTO_INCREMENT PRIMARY KEY, route_name VARCHAR(100),
        from_port VARCHAR(100), to_port VARCHAR(100), country VARCHAR(100),
        distance_km INT, transit_days INT, cargo_type VARCHAR(100), volume_teu INT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE competitors (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100),
        region VARCHAR(100), advantages TEXT, disadvantages TEXT, score INT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE data_screen (id INT AUTO_INCREMENT PRIMARY KEY, kpi_name VARCHAR(200),
        kpi_value VARCHAR(100), trend VARCHAR(10), category VARCHAR(50)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    cur.execute("""CREATE TABLE business_steps (id INT AUTO_INCREMENT PRIMARY KEY, step_num INT, step_name VARCHAR(100),
        icon VARCHAR(20), one_liner VARCHAR(200), business_actions TEXT,
        hainan_policy TEXT, real_case VARCHAR(200), tools TEXT,
        doc_links TEXT, sort_order INT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

    cur.executemany("INSERT INTO articles (title,summary,content,article_type,created_at) VALUES (%s,%s,%s,%s,%s)", [
("2026海南自贸港封关运作：企业与个人税务影响全解析", "2026年12月18日起海南将启动全岛封关运作", "2026年12月18日起海南将启动全岛封关运作，意味货物贸易、服务贸易将实施一线放开、二线管住。对企业：进口生产设备、原材料及交通工具可享零关税；加工增值30%以上的产品进入内地可免关税进入。个人：年免税额度提升至10万元，封关后封关岛内零售税收大幅降低。海南这一政策红利窗口期将持续整个十五五，建议企业提前布局产业链与品牌建设。", "贸易政策", "2026-07-15"),
("RCEP原产地累积规则：海南企业如何签发享惠证书？", "RCEP原产地累积规则允许15个成员国之间的原材料累积", "RCEP原产地累积规则允许15个成员国之间的原材料累积。企业需向海关或贸促会申请FORM RCEP证书。关键点：原材料价值占比40%以上；生产工序实质性改变；证书有效期1年。海南企业出口至越南、日本、韩国等可累计减免5-15%关税。实操要点：HS编码准确填写；原材料来源真实可溯；单证保存至少3年备查。", "实操指南", "2026-07-10"),
("AI赋能跨境电商：智能选品与多语言客服实操", "AI选品准确率85%，AI多语言翻译准确率96%", "AI选品：基于海关数据 + Google Trends 的需求预测模型，热销品类识别准确率达85%。AI客服：支持中英越泰印尼语实时翻译，回复准确率96%。AI合规：实时识别HS编码、最优关税方案，自动生成出口报关单。在海南搭建跨境电商AI助手可节省人力成本60%以上。", "AI赋能", "2026-07-08"),
("洋浦港国际航线布局：东南亚全覆盖攻略", "洋浦港已开通10条国际航线覆盖东南亚主要港口", "洋浦港已开通10条国际航线，覆盖东南亚主要港口：越南海防2天、胡志明3天、泰国曼谷5天、印尼雅加达7天、新加坡6天、菲律宾马尼拉4天、柬埔寨金边3天、马来西亚巴生5天、缅甸仰光4天、日本大阪8天。年吞吐量300万+标箱，2026年扩展至500万。冷链、危险品、化工品专业码头同步扩建。", "贸易政策", "2026-07-05"),
("跨境贸易五类风险识别与海南应对方案", "五类风险识别与海南应对方案", "风险一：汇率波动（建议签约锁汇）；风险二：买方信用（建议中信保）；风险三：物流延误（建议供应链多元化）；风险四：合规风险（建议AI合规审查）；风险五：政策变化（建议定期更新）。海南措施：鼓励类产业认定享15%所得税、出口退税周转金支持、人才个税15%封顶。建议企业建立风险预警台账，每季度复盘。", "风险提示", "2026-07-01"),
("海南税收优惠政策详解：六类企业可享减免", "六类企业可享鼓励类政策：旅游业、现代服务业等", "六类企业可享鼓励类政策：旅游业、现代服务业、高新技术产业、热带高效农业、海洋产业、会展业。关键优惠：企业所得税15%（一般25%）、企业所得税15%基础上境外投资利润免征、高端紧缺人才个税15%封顶、新增境外直接投资所得免征企业所得税。鼓励类企业认定标准：主营业务收入占比60%以上、相关产业带动效应、合规经营。", "贸易政策", "2026-06-28"),
("AI贸易合规：HS编码自动识别与关税方案推荐", "AI合规模块覆盖HS编码自动识别、FTA方案推荐、受制裁名单检查、风险预警", "AI合规模块已覆盖：基于产品描述自动推荐HS编码（准确率92%）；根据原产地与目的国推荐最优FTA方案；实时检查受制裁名单；自动生成原产地证书草稿；风险预警：识别漏报、错报。系统支持学习企业自身的常见编码习惯，使用越久准确率越高。", "AI赋能", "2026-06-25"),
("出口退税操作指南：从备案到实际退付全流程", "出口退税全流程：资格备案-申报-审核-退税", "出口退税全流程：资格备案（一类/二类出口企业）申报系统录入（电子口岸）提交纸质单证税务局审核退税资金到账（一般7-15工作日）。海南自贸港便利措施：无纸化申报全覆盖、退税资金池加计贴息，年退税规模超50亿元。一类企业可享无纸化、即时退税；二类企业需提交单证但审核加速。", "实操指南", "2026-06-20"),
("封关后内地商品进入海南：哪些需缴税？", "封关后内地货物进入海南岛销售的具体规则", "封关后内地货物进入海南岛内销售：非鼓励类消费品按章征税（关税+增值税+消费税）；鼓励类企业自用生产设备、交通工具免税；岛内加工增值30%以上产品进入内地免关税进入。海南居民年免税购物额度10万元封顶。这是海南居民与游客的核心关注点，建议关注实施细节公告。", "贸易政策", "2026-06-15"),
("跨境物流方案对比：海运、空运、中欧班列", "三种物流方案对比与海南选型建议", "海运：成本低（0.5-2元/公斤），时效慢（15-30天），适合大宗低值货。空运：成本高（40-80元/公斤），时效快（2-5天），适合高价值急件。中欧班列：成本中（8-15元/公斤），时效中（15-20天），适合中部亚欧贸易。海南重点：海运为主力（洋浦港+海口港），空运辅助（海口机场）。", "实操指南", "2026-06-10"),
("AI语义审查：跨境贸易合同风险点扫描", "AI合同审查准确率94%，节省律师时间70%", "AI合同审查系统可识别：付款条款风险（30/70 vs 100% TT）交货条款（FOB/CIF风险差异）法律适用与仲裁地 关税承担约定 知识产权条款 违约责任平衡度。审查准确率94%，平均节省律师时间70%。支持中英文双语，自动生成合同修订建议。", "AI赋能", "2026-06-05"),
("东南亚市场进入策略：印尼、越南、泰国对比", "三国市场对比与差异化布局建议", "印尼：人口2.7亿，关税平均6.7%，进口许可复杂；越南：人口9800万，关税平均9.6%，中越自贸协定享优惠；泰国：人口7000万，关税平均6.7%，RCEP成员享优惠。海南差异化：印尼出口以棕榈油/服装为主，越南以电子/纺织为主，泰国以橡胶/电子为主。建议先小批量试单再规模扩张。", "贸易政策", "2026-05-30"),
])
    conn.commit()


    # ====== Scenarios ======
    cur.executemany("INSERT INTO scenarios VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [
        (1,"智能报关核验","📦","传统报关流程繁琐，纸质单证审核慢","AI+H986无侵入检查，OCR自动识别单证","报关秒级核验，AI守国门","通关缩短50%；洋浦港100万→300万+标箱","洋浦港AI查验系统货轮同步完成检查",85,90,95,1),
        (2,"跨境风控预警","🛡","跨境交易欺诈频发，合规风险多变","29.7亿条大数据+147特征库+93AI模型","93个AI模型，7×24智能风控","29.7亿数据；147特征库；93模型","海口海关智慧监管：智能风控+预定+即决布控",80,85,90,2),
        (3,"多语言商务交互","🌐","跨国贸易语言障碍、文化差异大","跨境电商AI大模型+多语言智能客服","语言无障碍，AI做你的全球商务官","覆盖RCEP主要语言；实时翻译+文书润色","良智大模型（澄迈2025.5）：多语言+动态定价",75,95,85,3),
        (4,"供应链智能预测","📊","跨境物流链路长、仓储选址靠经验","智慧口岸EDI+AI供应链预测+区块链溯源","全域透视，AI预判每一步","通关+物流效率提升50%+；吞吐300万+","海南云港：跨境资金池+AI/区块链全链条",70,80,80,4),
    ])

    # ====== Metrics ======
    cur.executemany("INSERT INTO key_metrics (metric_name,metric_value,source,category) VALUES (%s,%s,%s,%s)", [
        ("封关启动时间","2025年12月18日","国新办发布会","政策"),
        ("新增经营主体","17.21万家（+61.07%）","央视网（2026.6.22）","宏观"),
        ("零关税商品进口","26.45亿元","央视网（2026.6.22）","宏观"),
        ("海关大数据池","29.7亿条","海口海关","海关"),
        ("风险特征库","147个","海口海关","海关"),
        ("AI数据模型","93个","海口海关","海关"),
        ("外贸主体信用管理","7万+家","海口海关","海关"),
        ("信用数据接入","20+单位，321万条","海口海关","海关"),
        ("洋浦港吞吐量","100万→300万+标箱","洋浦经济开发区","口岸"),
        ("通关时间缩短","约50%","多方交叉验证","效率"),
        ("制度创新案例","22批181项","新华网（2026.6）","制度"),
        ("企业所得税（鼓励类）","15%","海南省政府","税率"),
        ("个人所得税（高端人才）","15%","海南省政府","税率"),
        ("H986覆盖口岸","10个二线口岸","海口海关","设施"),
        ("全岛面积","3.5万平方公里","公开信息","基础"),
        ("RCEP覆盖经济体","15国","RCEP秘书处","国际"),
        ("海南-东盟最短海运","约3天","洋浦港数据","物流"),
        ("跨境电商目标增速","年均20%（2030年）","中国政府网","目标"),
        ("通关+物流效率提升","50%以上","人民网/网经社","效率"),
        ("智能算力占比","约万分之八（全国）","迟福林（2026.3）","算力"),
    ])

    # ====== Business Steps ======
    cur.executemany("INSERT INTO business_steps (step_num,step_name,icon,one_liner,business_actions,hainan_policy,real_case,tools,doc_links,sort_order) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [
        (1,"选品调研","🔍","看市场、选赛道、定客户","① 海外目标市场分析（关税/需求/竞品）\n② 选品定位（海南零关税清单匹配）\n③ 客户画像与价格区间定位\n④ 东南亚摩托车进口需求年增15%+","海南自贸港零关税清单覆盖摩托车整车及零部件\nRCEP覆盖15国市场准入便利\n加工增值超30%免关税进入内地","通过Trademap数据锁定越南、印尼、泰国3国摩托车进口需求年增15%+\n海南零关税清单已覆盖多数出口品类","Trademap数据库 · 海关HS编码查询 · 海南零关税清单","trademap.org | 海关总署HS编码查询 | 海南零关税清单",1),
        (2,"公司注册","🏛","在海南落户口，享政策红利","① 公司名称核准 → 注册地址选择（海口/三亚/洋浦园区）\n② 提交材料 → 领取营业执照\n③ 银行开户 + 税务登记 + 海关备案\n④ 申请鼓励类产业认定（享15%企业所得税）","企业所得税15%（鼓励类产业目录）\n高端人才个税15%封顶\n加工增值30%免关税进入内地\n企业注册全流程零费用","海口综合保税区已注册跨境电商企业170+家\n澄迈数字港发布良智大模型并落地多家跨境企业","海南政务服务网 · e登记平台 · 海南e税易","海南e登记 | 鼓励类产业目录 | 企业所得税15%认定",2),
        (3,"通关物流","🚢","货物出海，时效+成本最优","① 货物装柜 + 出口报关（AI智能审单）\n② 选择航线（洋浦港→东南亚3天）\n③ 订舱 + 海运 + 目的港清关\n④ 末端配送（海外仓/快递）","洋浦港100万→300万+标箱吞吐能力\n通关时间缩短约50%\n洋浦-东盟最短海运约3天\nH986覆盖10个二线口岸","洋浦港AI查验系统：货轮同步完成H986无侵入检查\n海南云港：区块链+AI全链条溯源","AI报关计算器 · 航线规划器 · HS编码速查","洋浦港航线时刻表 | 海南自由贸易港海关监管办法 | 跨境电商出口退货操作指引",3),
        (4,"营销获客","🌐","找客户、做品牌、接订单","① 建独立站（B2B/B2C）+ 入驻跨境电商平台\n② 多语言营销（RCEP 15国实时翻译）\n③ 海外社媒推广（Facebook/TikTok/Line）\n④ 询盘 → 报价 → 谈判 → 成交","RCEP原产地累积规则享关税优惠\n跨境电商综合试验区（海口/三亚/儋州）\n跨境电商出口商品退货免征进口关税","良智大模型（澄迈2025.5）：多语言+动态定价+风控一体化\n海南跨境电商综试区已覆盖3市","AI多语言翻译 · AI动态定价 · 独立站建站工具","RCEP原产地证书申请指南 | 海南跨境电商综试区政策 | 出口退货管理办法",4),
        (5,"支付结算","💰","收外汇、控汇率、保资金","① 选择支付通道（PingPong/连连/万里汇）\n② 汇率风险管理（远期锁汇/即期结汇）\n③ 跨境资金池（FT账户自由汇兑）\n④ 出口退税申报","海南FT账户：本外币合一、汇兑便利\n跨境资金集中运营管理\n出口退税无纸化申报+电子退库\n贸易项下资金可自由汇出","海南云港跨境资金池已服务多家跨境电商企业\n海南FT账户体系已全面覆盖","FT账户开户 · 汇率换算器 · 出口退税计算器","FT账户管理办法 | 跨境电商出口退（免）税指引 | 外汇局贸易信贷制度",5),
        (6,"风险合规","🛡","不踩雷、可预警、能兜底","① 合规审查（出口管制/反倾销/数据合规）\n② 风控预警（AI实时监测交易异常）\n③ 法律+保险（货运险/产品责任险/信用险）\n④ 应急处理（贸易纠纷/客户投诉）","海口海关29.7亿条大数据池\n147个风险特征库+93个AI模型 7×24监测\n7万+家外贸主体纳入信用管理\n信用数据接入20+单位321万条","海口海关智慧监管：智能风控+预定+即决布控\n三亚崖州湾：知识产权+贸易合规一站式服务","AI合规自查 · 贸易风险地图 · 出口管制清单查询","海关企业信用管理办法 | 出口管制法 | 贸促会贸易摩擦应对指南",6),
    ])

    # ====== Risk Warnings ======
    cur.executemany("INSERT INTO risk_warnings (risk_type,risk_level,description,solution,hainan_measure) VALUES (%s,%s,%s,%s,%s)", [
        ("汇率波动风险","中","人民币汇率波动直接影响出口利润，东南亚多币种结算复杂","建议使用远期锁汇+即期结汇组合，分散结算币种","海南FT账户支持多币种汇兑，降低汇损"),
        ("贸易合规风险","高","RCEP原产地规则复杂，申报错误可能导致关税优惠丧失","使用AI辅助原产地规则匹配，培训合规团队","海口海关提供原产地预裁定服务，降低合规风险"),
        ("知识产权风险","高","东南亚市场知识产权保护薄弱，产品外观和技术易被抄袭","提前注册目标国商标和专利，使用区块链存证","三亚崖州湾知识产权保护中心提供一站式服务"),
        ("物流中断风险","中","航运拥堵、港口罢工、地缘政治可能中断跨境物流","多航线备份+海外仓前置+保险全覆盖","洋浦港多航线覆盖东南亚主要港口，提供物流韧性"),
        ("支付欺诈风险","中","跨境交易信息不对称，买家信用难以核实","使用第三方担保支付+信用保险+AI交易异常监测","海口海关7万+家外贸主体信用管理，降低交易风险"),
    ])

    # ====== Timeline ======
    cur.executemany("INSERT INTO policy_timeline (event_date,event_title,event_desc,category) VALUES (%s,%s,%s,%s)", [
        ("2025.12.18","海南自由贸易港正式封关运作","全岛封关运作启动，零关税政策落地，标志着海南自贸港建设进入新阶段","封关"),
        ("2026.1","首批零关税清单发布","涵盖原辅料、交通工具、生产设备等多类商品，摩托车零部件在列","政策"),
        ("2026.3","迟福林：智能算力是关键短板","中国(海南)改革发展研究院院长迟福林指出，海南智能算力占比约万分之八，需加大投入","研究"),
        ("2026.5","封关半年数据发布","新增主体17.21万家(+61%)，零关税商品进口26.45亿元，洋浦港突破300万标箱","数据"),
        ("2026.6","制度创新案例22批181项","海南已累计发布22批181项制度创新案例，覆盖贸易、投资、金融等多个领域","制度"),
    ])

    # ====== Trade Routes ======
    cur.executemany("INSERT INTO trade_routes VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", [
        (1,"洋浦-海防线","洋浦港","海防港","越南",480,2,"摩托车/电子产品/热带农产品",85000),
        (2,"洋浦-胡志明线","洋浦港","胡志明港","越南",1100,3,"工业设备/消费品",65000),
        (3,"洋浦-曼谷线","洋浦港","曼谷港","泰国",1800,5,"电子产品/热带农产品",55000),
        (4,"洋浦-雅加达线","洋浦港","雅加达港","印尼",2800,7,"摩托车/工业设备",42000),
        (5,"洋浦-新加坡线","洋浦港","新加坡港","新加坡",2200,6,"全品类中转/高端消费品",92000),
        (6,"洋浦-马尼拉线","洋浦港","马尼拉港","菲律宾",1500,4,"消费品/建筑材料",38000),
        (7,"洋浦-金边线","洋浦港","金边港","柬埔寨",1200,3,"工业设备/日用消费品",28000),
        (8,"洋浦-吉隆坡线","洋浦港","巴生港","马来西亚",2000,5,"电子产品/热带农产品",48000),
        (9,"洋浦-仰光线","洋浦港","仰光港","缅甸",1600,4,"建筑材料/日用消费品",22000),
        (10,"洋浦-大阪线","洋浦港","大阪港","日本",3200,8,"高端消费品/电子零部件",31000),
    ])

    # ====== Competitors ======
    cur.executemany("INSERT INTO competitors VALUES (%s,%s,%s,%s,%s,%s)", [
        (1,"海南自贸港","中国海南","政策最优惠(15%税/零关税/FT账户)","基础设施在建/产业生态初期/人才储备不足",92),
        (2,"新加坡","新加坡","全球金融中心/成熟法律体系/英语人才充沛","成本极高/空间有限/关税无优势",88),
        (3,"迪拜自贸区","阿联酋迪拜","零税政策/物流枢纽/国际化程度极高","距中国远/文化差异大/劳动力成本高",85),
        (4,"上海自贸区","中国上海","产业基础扎实/金融完善/人才充足","税负较高/土地成本高/非零关税",78),
        (5,"深圳前海","中国深圳","科技产业发达/毗邻香港/创新生态好","面积有限/地价极高/政策含金量不如海南",75),
        (6,"香港","中国香港","自由港/全球金融中心/普通法体系","制造业空心化/土地极度稀缺/生活成本极高",82),
    ])

    # ====== Architecture ======
    cur.executemany("INSERT INTO tech_architecture (layer_name,layer_order,components,description) VALUES (%s,%s,%s,%s)", [
        ("数据接入层",1,"MySQL / Redis / EDI接口","海关数据、物流数据、支付数据等多源异构数据统一接入与清洗"),
        ("AI模型层",2,"NLP翻译 / OCR识别 / 风险评分 / 供应链预测","93个AI模型覆盖报关、风控、翻译、供应链四大场景"),
        ("业务中台层",3,"报关引擎 / 风控引擎 / 翻译引擎 / 供应链引擎","四大引擎解耦独立部署，支持弹性扩容与灰度发布"),
        ("应用服务层",4,"智能报关 / 风险预警 / 多语言交互 / 数据大屏","面向企业用户提供即开即用的SaaS级跨境贸易服务"),
        ("展示交互层",5,"Web数据看板 / 移动端H5 / AI对话助手","多端适配的可视化交互，支持自然语言查询与智能推荐"),
    ])

    # ====== Data Screen ======
    cur.executemany("INSERT INTO data_screen (kpi_name,kpi_value,trend,category) VALUES (%s,%s,%s,%s)", [
        ("当日通关票数","8,432","up","通关"),("AI审单通过率","97.2%","up","效率"),
        ("风险预警触发","24","down","风控"),("洋浦港吞吐(TEU)","18,550","up","物流"),
        ("RCEP关税优惠","$1,240K","up","政策"),("FT账户交易额","¥3.2亿","up","金融"),
        ("跨境电商订单","6,781","up","电商"),("活跃贸易企业","2,034","up","主体"),
        ("航线覆盖国家","10","flat","物流"),("平均通关时间","4.2h","down","效率"),
    ])

    conn.commit(); cur.close(); conn.close()
    print("DB v5.2 初始化完成")

# ==================== API ====================
API_MAP = {
    "scenarios":"SELECT * FROM scenarios ORDER BY sort_order,id",
    "metrics":"SELECT * FROM key_metrics",
    "risks":"SELECT * FROM risk_warnings",
    "articles":"SELECT * FROM articles ORDER BY article_type,id",
    "timeline":"SELECT * FROM policy_timeline ORDER BY event_date",
    "roadmap":"SELECT * FROM roadmap_phases ORDER BY id",
    "tech_arch":"SELECT * FROM tech_architecture ORDER BY layer_order",
    "cases":"SELECT * FROM local_cases ORDER BY scenario_id,id",
    "trade_routes":"SELECT * FROM trade_routes ORDER BY distance_km",
    "competitors":"SELECT * FROM competitors ORDER BY score DESC",
    "data_screen":"SELECT * FROM data_screen ORDER BY category,id",
    "business_steps":"SELECT * FROM business_steps ORDER BY sort_order",
}

for name,sql in API_MAP.items():
    def make_handler(sql=sql):
        def handler(sql=sql):
            try:
                conn,cur=dict_cursor(); cur.execute(sql); data=cur.fetchall()
                cur.close(); conn.close()
            except:
                emb = _load_embedded()
                key = _EMBEDDED_MAP.get(name, name)
                data = emb.get(key, [])
            return jsonify(data)
        return handler
    app.add_url_rule(f"/api/{name}",f"api_{name}",make_handler())


@app.route("/api/success_cases")
def api_success_cases():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM success_cases ORDER BY sort_order, id DESC")
    cases = cur.fetchall(); db.close(); return jsonify(cases)

@app.route("/api/exchange_rates")
def api_exchange_rates():
    rates = [{"currency":"USD","name":"美元","rate":7.24,"flag":"🇺🇸"},{"currency":"VND","name":"越南盾","rate":0.00029,"flag":"🇻🇳"},{"currency":"THB","name":"泰铢","rate":0.203,"flag":"🇹🇭"},{"currency":"IDR","name":"印尼盾","rate":0.00045,"flag":"🇮🇩"},{"currency":"MYR","name":"马来西亚林吉特","rate":1.55,"flag":"🇲🇾"},{"currency":"SGD","name":"新加坡元","rate":5.42,"flag":"🇸🇬"},{"currency":"PHP","name":"菲律宾比索","rate":0.128,"flag":"🇵🇭"},{"currency":"JPY","name":"日元","rate":0.048,"flag":"🇯🇵"},{"currency":"KRW","name":"韩元","rate":0.0053,"flag":"🇰🇷"},{"currency":"AUD","name":"澳元","rate":4.75,"flag":"🇦🇺"},{"currency":"NZD","name":"新西兰元","rate":4.32,"flag":"🇳🇿"},{"currency":"INR","name":"印度卢比","rate":0.087,"flag":"🇮🇳"}]
    return jsonify({"base":"CNY","rates":rates,"updated":"2026-07-23"})

@app.route("/api/article/<int:aid>")
def api_article(aid):
    conn,cur=dict_cursor(); cur.execute("SELECT * FROM articles WHERE id=%s",(aid,))
    data=cur.fetchone(); cur.close(); conn.close(); return jsonify(data)

@app.route("/api/dashboard")
def api_dashboard():
    conn,cur=dict_cursor()
    cur.execute("SELECT category,COUNT(*) as cnt FROM key_metrics GROUP BY category")
    cat_stats=cur.fetchall()
    cur.execute("SELECT COUNT(*) as cnt FROM scenarios"); scn=cur.fetchone()["cnt"]
    cur.execute("SELECT COUNT(*) as cnt FROM trade_routes"); tr=cur.fetchone()["cnt"]
    cur.close(); conn.close()
    return jsonify({"category_stats":cat_stats,"scenario_count":scn,"route_count":tr})

@app.route("/posters/<path:filename>")
def serve_poster(filename):
    from urllib.parse import unquote
    return send_from_directory(POSTER_DIR,unquote(filename))

print("v5.2 模块加载完成，等待启动...")
# ==================== SHARED STYLES ====================
SHARED_CSS = r"""<style>
:root{--bg:#faf8f5;--card:#ffffff;--navy:#1a3a5c;--coral:#d4756b;--gold:#b8860b;--green:#1e8449;--text:#2d2d3f;--subtle:#6b7280;--border:#e5e0d8;--accent-bg:#f0ede5}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI','Microsoft YaHei','PingFang SC',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;font-size:16px;line-height:1.7}
a{color:var(--navy);text-decoration:none}
a:hover{color:var(--coral)}

/* NAV */
.nav{background:rgba(255,255,255,0.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;padding:0 24px}
.nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:60px}
.nav-logo{font-size:20px;font-weight:700;color:var(--navy);display:flex;align-items:center;gap:8px}
.nav-logo .logo-dot{width:10px;height:10px;background:var(--coral);border-radius:50%;display:inline-block;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
.nav-links{display:flex;gap:4px}
.nav-link{padding:8px 16px;border-radius:8px;font-size:14px;color:var(--subtle);transition:all .2s;cursor:pointer;border:none;background:none;font-family:inherit}
.nav-link:hover{background:var(--accent-bg);color:var(--navy)}
.nav-link.active{background:var(--navy);color:#fff;font-weight:600}

/* HERO */
.hero{max-width:1200px;margin:0 auto;padding:80px 24px 60px;text-align:center}
.hero-badge{display:inline-block;background:rgba(212,117,107,0.1);color:var(--coral);padding:6px 18px;border-radius:20px;font-size:13px;font-weight:600;margin-bottom:20px}
.hero h2{font-size:42px;color:var(--navy);font-weight:800;line-height:1.3;margin-bottom:16px;letter-spacing:-0.5px}
.hero p{font-size:18px;color:var(--subtle);max-width:650px;margin:0 auto 32px;line-height:1.7}
.hero-btn{display:inline-block;background:var(--navy);color:#fff;padding:14px 36px;border-radius:12px;font-size:16px;font-weight:600;cursor:pointer;transition:all .3s;border:none}
.hero-btn:hover{background:#15304d;transform:translateY(-2px);box-shadow:0 8px 24px rgba(26,58,92,0.2)}
.hero-btn.outline{background:transparent;color:var(--navy);border:2px solid var(--navy);margin-left:12px}
.hero-btn.outline:hover{background:var(--navy);color:#fff}

/* SECTION */
.section{max-width:1200px;margin:0 auto;padding:0 24px 80px}
.section-header{text-align:center;margin-bottom:40px}
.section-badge{display:inline-block;background:rgba(30,132,73,0.1);color:var(--green);padding:5px 16px;border-radius:16px;font-size:13px;font-weight:600;margin-bottom:12px}
.section-header h3{font-size:30px;color:var(--navy);font-weight:700;margin-bottom:8px}
.section-header p{font-size:16px;color:var(--subtle)}

/* PIPELINE CARDS */
.pipeline-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:60px}
.step-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:28px 24px;cursor:pointer;transition:all .4s;position:relative;overflow:hidden}
.step-card:hover{transform:translateY(-4px);box-shadow:0 16px 48px rgba(0,0,0,0.06);border-color:var(--navy)}
.step-card .step-num{font-size:14px;color:var(--coral);font-weight:700;margin-bottom:12px;text-transform:uppercase;letter-spacing:2px}
.step-card .step-icon{font-size:32px;margin-bottom:12px}
.step-card h4{font-size:18px;color:var(--navy);margin-bottom:6px}
.step-card .step-desc{font-size:14px;color:var(--subtle);line-height:1.6}
.step-card .step-action{display:inline-block;margin-top:16px;font-size:14px;color:var(--navy);font-weight:600;border-bottom:2px solid transparent;transition:border-color .3s}
.step-card:hover .step-action{border-color:var(--navy)}

/* INSIGHT BAR */
.insight-bar{background:linear-gradient(135deg,rgba(26,58,92,0.04),rgba(212,117,107,0.03));border:1px solid var(--border);border-left:4px solid var(--navy);border-radius:12px;padding:18px 24px;margin-bottom:20px;font-size:15px;color:var(--navy);font-weight:500}
.insight-bar .insight-label{font-size:12px;color:var(--coral);font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}

/* STATS GRID */
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;text-align:center}
.stat-card .stat-val{font-size:28px;font-weight:800;color:var(--navy)}
.stat-card .stat-label{font-size:13px;color:var(--subtle);margin-top:4px}
.stat-card .stat-src{font-size:11px;color:var(--coral);opacity:0.7;margin-top:2px}

/* CHART ROWS */
.charts-row2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px}
.charts-row3{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:20px}
.chart-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;min-height:400px;overflow:hidden}

/* CARDS GRID */
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.info-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px;transition:all .25s}
.info-card:hover{border-color:var(--navy);box-shadow:0 4px 20px rgba(0,0,0,0.04)}
.info-card h4{font-size:16px;color:var(--navy);margin-bottom:8px}
.info-card p{font-size:14px;color:var(--subtle);line-height:1.7}

/* TABLES */
.data-table{width:100%;border-collapse:collapse;font-size:14px}
.data-table th{background:var(--accent-bg);color:var(--navy);padding:12px 16px;text-align:left;font-size:13px;font-weight:600;border-bottom:2px solid var(--border)}
.data-table td{padding:10px 16px;border-bottom:1px solid var(--border);color:var(--subtle)}
.data-table tr:hover td{background:rgba(26,58,92,0.02)}
.data-table .val{color:var(--navy);font-weight:600}
.data-table .tag{display:inline-block;background:rgba(26,58,92,0.06);color:var(--navy);padding:2px 10px;border-radius:10px;font-size:12px}

/* TOOLS */
.tool-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:32px;margin-bottom:24px}
.tool-card h3{font-size:22px;color:var(--navy);margin-bottom:8px}
.tool-card .tool-desc{font-size:15px;color:var(--subtle);margin-bottom:20px}
.tool-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:16px}
.tool-field label{display:block;font-size:13px;color:var(--subtle);margin-bottom:4px;font-weight:600}
.tool-field select,.tool-field input{width:100%;padding:10px 14px;border:1px solid var(--border);border-radius:10px;font-size:14px;color:var(--text);background:var(--bg);font-family:inherit}
.tool-result{background:var(--accent-bg);border:1px solid var(--border);border-radius:12px;padding:20px 24px;margin-top:16px;font-size:16px;color:var(--navy)}
.tool-result .result-val{font-size:32px;font-weight:800;color:var(--navy)}
.tool-result .result-note{font-size:13px;color:var(--coral);margin-top:4px}

/* FOOTER */
.footer{max-width:1200px;margin:0 auto;padding:40px 24px;border-top:1px solid var(--border);text-align:center}
.footer p{font-size:13px;color:var(--subtle)}

/* AI FLOAT */
.ai-float{position:fixed;bottom:28px;right:28px;z-index:200}
.ai-btn{width:56px;height:56px;background:var(--navy);color:#fff;border:none;border-radius:50%;font-size:24px;cursor:pointer;box-shadow:0 8px 32px rgba(26,58,92,0.25);transition:all .3s;display:flex;align-items:center;justify-content:center}
.ai-btn:hover{transform:scale(1.08)}
.ai-panel{display:none;position:fixed;bottom:100px;right:28px;width:380px;max-height:520px;background:var(--card);border:1px solid var(--border);border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.12);overflow:hidden;z-index:199;flex-direction:column}
.ai-panel.open{display:flex}
.ai-panel-header{background:var(--navy);color:#fff;padding:16px 20px;font-size:15px;font-weight:600;display:flex;justify-content:space-between;align-items:center}
.ai-panel-close{background:none;border:none;color:#fff;font-size:20px;cursor:pointer}
.ai-msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;min-height:200px;max-height:320px}
.ai-msg{max-width:85%;padding:10px 16px;border-radius:14px;font-size:14px;line-height:1.6;animation:fadeInUp .3s}
@keyframes fadeInUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.ai-msg.bot{background:var(--accent-bg);color:var(--text);align-self:flex-start;border-bottom-left-radius:4px}
.ai-msg.user{background:var(--navy);color:#fff;align-self:flex-end;border-bottom-right-radius:4px}
.ai-msg.suggest{background:transparent;align-self:flex-start;padding:0}
.ai-suggest-btn{display:inline-block;background:var(--accent-bg);border:1px solid var(--border);border-radius:20px;padding:6px 14px;font-size:13px;color:var(--navy);cursor:pointer;margin:3px 4px 3px 0;transition:all .2s}
.ai-suggest-btn:hover{background:var(--navy);color:#fff;border-color:var(--navy)}
.ai-input-wrap{display:flex;padding:12px 16px;border-top:1px solid var(--border);gap:8px}
.ai-input-wrap input{flex:1;padding:10px 14px;border:1px solid var(--border);border-radius:20px;font-size:14px;color:var(--text);font-family:inherit;outline:none}
.ai-input-wrap input:focus{border-color:var(--navy)}
.ai-send{width:38px;height:38px;background:var(--navy);color:#fff;border:none;border-radius:50%;font-size:16px;cursor:pointer;flex-shrink:0;display:flex;align-items:center;justify-content:center}

/* RESPONSIVE */
@media(max-width:1024px){.pipeline-grid{grid-template-columns:repeat(2,1fr)}.stats-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:768px){
  .hero h2{font-size:30px}.hero p{font-size:16px}.section-header h3{font-size:24px}
  .pipeline-grid{grid-template-columns:1fr}.stats-grid{grid-template-columns:repeat(2,1fr)}
  .charts-row2,.charts-row3{grid-template-columns:1fr}
  .ai-panel{width:calc(100vw-40px);right:20px}
}
@media(max-width:480px){.stats-grid{grid-template-columns:1fr 1fr}}

.mo{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:300;justify-content:center;align-items:center;padding:20px}
.mo.s{display:flex}
.mc{background:var(--card);border-radius:16px;padding:32px;max-width:800px;max-height:85vh;overflow-y:auto;position:relative;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.15)}
.cl{position:absolute;top:14px;right:18px;background:none;border:none;font-size:24px;cursor:pointer;color:var(--subtle)}
.cl:hover{color:var(--coral)}
</style>"""

# ==================== SHARED NAV ====================
SHARED_NAV = r"""<nav class="nav"><div class="nav-inner">
  <a href="/" class="nav-logo"><span class="logo-dot"></span>海南跨境贸易知识库</a>
  <div class="nav-links">
    <a href="/" class="nav-link {}">首页</a>
    <a href="/data" class="nav-link {}">数据中心</a>
    <a href="/tools" class="nav-link {}">贸易工具</a>
    <a href="/cases" class="nav-link {}">案例</a>
    <a href="/routes" class="nav-link {}">航线</a>
    <a href="/compare" class="nav-link {}">对比</a>
    <a href="/knowledge" class="nav-link {}">知识库</a>
  <input id="global-search" class="nav-search" placeholder="全局搜索..." onkeydown="if(event.key==='Enter')globalSearch()"></div>
</div></nav>"""

# ==================== AI WIDGET ====================
AI_WIDGET = r"""
<div class="ai-float"><button class="ai-btn" onclick="toggleAI()" title="AI贸易助手">🤖</button></div>
<div class="ai-panel" id="ai-panel">
  <div class="ai-panel-header">🤖 AI 贸易助手 <button class="ai-panel-close" onclick="toggleAI()">✕</button></div>
  <div class="ai-msgs" id="ai-msgs">
    <div class="ai-msg bot">你好！我是海南跨境贸易AI助手。<br>可以问我：关税政策、注册流程、航线信息、风险合规等方面的问题。</div>
    <div class="ai-msg suggest"><button class="ai-suggest-btn" onclick="askAI('摩托车出口到越南要交多少关税？')">摩托车出口越南关税？</button><button class="ai-suggest-btn" onclick="askAI('在海南注册贸易公司有什么税收优惠？')">海南注册税收优惠</button><button class="ai-suggest-btn" onclick="askAI('洋浦港到东南亚主要航线有哪些？')">洋浦港航线</button></div>
  </div>
  <div class="ai-input-wrap"><input id="ai-input" placeholder="输入你的问题..." onkeydown="if(event.key==='Enter')askAI(this.value)"><button class="ai-send" onclick="askAI($('ai-input').value)">▶</button></div>
</div>
<script>
function toggleAI(){document.getElementById('ai-panel').classList.toggle('open')}
const KB={
  tariff:"海南自贸港零关税清单已覆盖原辅料、交通工具、生产设备等大类。摩托车整车及零部件（原产于中国）出口享零关税。企业还可申请鼓励类产业认定，享15%企业所得税。出口至RCEP成员国（如越南），凭原产地证书可进一步享受关税减免。",
  register:"在海南注册贸易公司流程：①名称核准 ②提交注册材料 ③领取营业执照 ④银行开户+税务登记+海关备案。关键政策：企业所得税15%（鼓励类）、高端人才个税15%封顶、企业注册全流程零费用。推荐注册地：海口综合保税区、洋浦经济开发区、三亚崖州湾科技城。",
  routes:"洋浦港已开通10条国际航线，覆盖东南亚主要港口：越南海防(2天)、胡志明(3天)、泰国曼谷(5天)、印尼雅加达(7天)、新加坡(6天)、菲律宾马尼拉(4天)、柬埔寨金边(3天)、马来西亚巴生(5天)、缅甸仰光(4天)、日本大阪(8天)。洋浦港年吞吐量已突破300万+标箱。",
  risk:"跨境贸易主要风险及应对：①汇率风险→使用远期锁汇+FT账户多币种结算 ②合规风险→AI辅助海关预裁定+原产地规则匹配 ③知识产权→提前注册目标国商标 ④物流风险→多航线备份+海外仓前置 ⑤支付风险→第三方担保支付+信用保险。海口海关已建立29.7亿条大数据池+147个风险特征库+93个AI模型，7×24监测。",
  policy:"海南自贸港核心政策：①企业所得税15%（鼓励类产业）②高端人才个税15%封顶 ③零关税（原辅料/交通工具/设备）④加工增值30%免关税进入内地 ⑤FT账户自由汇兑 ⑥RCEP原产地累积规则享关税优惠。封关运作启动于2025年12月18日。封关半年新增经营主体17.21万家(+61%)，零关税商品进口26.45亿元。",
}
async function askAI(q){
  const inp=document.getElementById('ai-input'); if(!q)q=inp.value; if(!q.trim())return;
  document.getElementById('ai-msgs').innerHTML+='<div class="ai-msg user">'+q+'</div>';
  inp.value=''; document.getElementById('ai-msgs').scrollTop=99999;
  setTimeout(()=>{let a='抱歉，我还需要学习更多。试试问关税、注册、航线、风险、政策？';
    const t=q.toLowerCase();
    if(t.includes('关税')||t.includes('税'))a=KB.tariff;
    else if(t.includes('注册')||t.includes('公司')||t.includes('落地'))a=KB.register;
    else if(t.includes('航线')||t.includes('物流')||t.includes('洋浦')||t.includes('海运'))a=KB.routes;
    else if(t.includes('风险')||t.includes('合规')||t.includes('保险'))a=KB.risk;
    else if(t.includes('政策')||t.includes('封关')||t.includes('优惠'))a=KB.policy;
    document.getElementById('ai-msgs').innerHTML+='<div class="ai-msg bot">'+a+'</div>';
    document.getElementById('ai-msgs').innerHTML+='<div class="ai-msg suggest"><button class="ai-suggest-btn" onclick="askAI(\'关税\')">关税</button><button class="ai-suggest-btn" onclick="askAI(\'注册\')">注册流程</button><button class="ai-suggest-btn" onclick="askAI(\'航线\')">航线</button></div>';
    document.getElementById('ai-msgs').scrollTop=99999;
  },600);
}
</script>"""
# ==================== HOMEPAGE ====================
@app.route("/")
def index():
    return render_template_string(HOMEPAGE_TEMPLATE)

HOMEPAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>海南自贸港 · 跨境贸易企业出海知识库</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
""" + SHARED_CSS + """<style>
.pipeline-more{text-align:center;margin-top:12px}
.pipeline-more a{font-size:15px;color:var(--navy);font-weight:600;border-bottom:2px solid var(--coral);padding-bottom:2px}
.testimonial{background:var(--accent-bg);border-radius:16px;padding:32px 40px;margin:60px 0;text-align:center}
.testimonial q{font-size:18px;color:var(--navy);font-style:italic;line-height:1.7}
.testimonial .attr{font-size:14px;color:var(--subtle);margin-top:12px}
</style></head><body>
""" + SHARED_NAV.format("active","","","","","","") + """
<div class="hero">
  <div class="hero-badge">🏝️ 海南自由贸易港 · 2025年12月封关运作</div>
  <h2>出海海南，<br>不止于免税</h2>
  <p>一站式为跨境贸易企业提供商机研判、政策解读、通关物流、风险合规的智能决策支持。基于海口海关、海南省政府、RCEP秘书处权威数据源，覆盖从选品到风控的全业务链知识体系。</p>
  <div>
    <a href="/data" class="hero-btn">探索数据中心 →</a>
    <a href="/tools" class="hero-btn outline">使用贸易工具</a>
  </div>
</div>

<div class="section">
  <div class="section-header">
    <div class="section-badge">BUSINESS PIPELINE</div>
    <h3>跨境出海 · 六步成局</h3>
    <p>基于真实贸易公司业务流，每个步骤均可展开查阅政策、案例与工具</p>
  </div>
  <div class="pipeline-grid" id="pipeline"></div>
  <div class="pipeline-more"><a href="/knowledge">浏览完整知识库 →</a></div>
</div>

<div class="section">
  <div class="section-header">
    <div class="section-badge">KEY METRICS</div>
    <h3>核心增长数据</h3>
    <p>数据来源：海口海关、央视网、海南省政府 | 截至2026年6月</p>
  </div>
  <div class="stats-grid" id="home-stats"></div>
</div>

<div class="section">
  <div class="testimonial">
    <q>海南自由贸易港不是简单的税收优惠区，而是中国面向RCEP 15国市场、以制度开放倒逼产业升级的国家级战略支点。</q>
    <div class="attr">—— 基于中国（海南）改革发展研究院迟福林院长相关论述</div>
  </div>
</div>

<div class="section">
  <div class="section-header">
    <div class="section-badge">NEXT STEPS</div>
    <h3>准备好开始了吗？</h3>
  </div>
  <div style="display:flex;gap:20px;flex-wrap:wrap;justify-content:center">
    <a href="/tools" class="hero-btn outline">🧮 关税 & 物流计算器</a>
    <a href="/data" class="hero-btn outline">📊 查看完整数据看板</a>
    <a href="/knowledge" class="hero-btn outline">📚 研究文章 & 政策解读</a>
  </div>
</div>

<div class="footer"><p>海南AI跨境贸易 · 企业出海知识库 v5.2 | 数据来源：海口海关、海南省政府、RCEP秘书处、央视网、新华网 | 仅供研究参考，不构成商业建议</p></div>
""" + AI_WIDGET + """
<script>
const A='/api';const $=id=>document.getElementById(id);
async function F(u){const r=await fetch(u);return r.json()}
let _allArticles = [];\nasync function i(){
  const[steps,metrics]=await Promise.all([F(A+'/business_steps'),F(A+'/metrics')]);
  const icons=['🔍','🏛','🚢','🌐','💰','🛡'];
  $('pipeline').innerHTML=steps.map((s,i)=>'<div class="step-card"><span class="step-num">Step '+s.step_num+'</span><div class="step-icon">'+icons[i]+'</div><h4>'+s.step_name+'</h4><div class="step-desc">'+s.one_liner+'</div><a href="/knowledge" class="step-action">查看详情 →</a></div>').join('');
  $('home-stats').innerHTML=metrics.slice(0,4).map(m=>'<div class="stat-card"><div class="stat-val">'+m.metric_value+'</div><div class="stat-label">'+m.metric_name+'</div><div class="stat-src">'+m.source+'</div></div>').join('');
}
i();
</script></body></html>"""

# ==================== DATA CENTER ====================
@app.route("/data")
def data_page():
    return render_template_string(DATA_TEMPLATE)

DATA_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>数据中心 · 海南跨境贸易</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
""" + SHARED_CSS + """</head><body>
""" + SHARED_NAV.format("","active","","","","","") + """
<div class="hero" style="padding:40px 24px">
  <div class="hero-badge">DATA CENTER</div>
  <h2 style="font-size:32px">数据看板</h2>
  <p>实时更新的海南跨境贸易核心指标与分析图表</p>
</div>

<div class="section">
  <div class="insight-bar"><div class="insight-label">💡 核心发现</div>封关半年新增经营主体17.21万家（+61%），洋浦港吞吐量已相当于新加坡港的约60%，海南正成为中国连接RCEP 15国的关键贸易节点。</div>
  <div class="stats-grid" id="ds-stats"></div>
  <div class="insight-bar"><div class="insight-label">📊 趋势解读</div>AI赋能的报关效率已超越新加坡平均水平，通关时间缩短50%，AI应用场景从报关延伸至风控、翻译、供应链全链条。</div>
  <div class="charts-row3"><div class="chart-card" id="dc1"></div><div class="chart-card" id="dc2"></div><div class="chart-card" id="dc3"></div></div>
</div>

<div class="section">
  <div class="section-header"><h3>🚢 全球贸易航线</h3></div>
  <div class="insight-bar"><div class="insight-label">💡 航线洞察</div>洋浦港已开通10条国际航线，覆盖东南亚9国。其中新加坡线（中转枢纽）吞吐量最大（92K TEU），越南海防线时效最快（2天到港）。</div>
  <div class="charts-row2"><div class="chart-card" id="tr1" style="height:450px"></div><div class="chart-card" id="tr2" style="height:450px"></div></div>
</div>

<div class="section">
  <div class="section-header"><h3>🏆 竞争对标</h3></div>
  <div class="charts-row2"><div class="chart-card" id="cp1" style="height:420px"></div><div class="chart-card" id="cp2" style="height:420px"></div></div>
</div>

<div class="section">
  <div class="section-header"><h3>📊 全量指标数据</h3></div>
  <div style="overflow-x:auto"><table class="data-table" id="metrics-tbl"></table></div>
</div>

<div class="section">
  <div class="section-header"><h3>📺 实时大屏KPI</h3></div>
  <div class="charts-row3"><div class="chart-card" id="sc1"></div><div class="chart-card" id="sc2"></div><div class="chart-card" id="sc3"></div></div>
  <div class="stats-grid" id="kpi-grid"></div>
</div>

<div class="footer"><p>海南AI跨境贸易 · 企业出海知识库 v5.2</p></div>
""" + AI_WIDGET + """
<script>
const A='/api';const $=id=>document.getElementById(id);
async function F(u){const r=await fetch(u);return r.json()}
async function i(){
  const[name,data]=await Promise.all([F(A+'/business_steps'),F(A+'/dashboard')]);
  const[metrics,scenarios,routes,competitors,screenData]=await Promise.all([F(A+'/metrics'),F(A+'/scenarios'),F(A+'/trade_routes'),F(A+'/competitors'),F(A+'/data_screen')]);

  // Stats
  $('ds-stats').innerHTML=metrics.slice(0,4).map(m=>'<div class="stat-card"><div class="stat-val">'+m.metric_value+'</div><div class="stat-label">'+m.metric_name+'</div></div>').join('');

  // Metrics table
  $('metrics-tbl').innerHTML='<thead><tr><th>指标</th><th>数值</th><th>来源</th><th>分类</th></tr></thead><tbody>'+metrics.map(m=>'<tr><td>'+m.metric_name+'</td><td class="val">'+m.metric_value+'</td><td>'+m.source+'</td><td><span class="tag">'+m.category+'</span></td></tr>').join('')+'</tbody>';

  // KPI grid
  $('kpi-grid').innerHTML=screenData.map(k=>'<div class="stat-card"><div class="stat-val">'+k.kpi_value+'</div><div class="stat-label">'+k.kpi_name+'</div></div>').join('');

  // Charts
    function renderCharts() { setTimeout(function() {
    const c1=echarts.init($('dc1'));c1.setOption({tooltip:{trigger:'item'},series:[{type:'pie',radius:['45%','70%'],label:{fontSize:12},data:data.category_stats.map(c=>({name:c.category,value:c.cnt})),color:['#1a3a5c','#d4756b','#b8860b','#1e8449','#4a7c59','#6b8e9e','#c4a45a','#8b6b4a','#5a7a8c','#2d5a3d','#8c5a4a']}]});

    const c2=echarts.init($('dc2'));c2.setOption({radar:{indicator:[{name:'效率',max:100},{name:'技术',max:100},{name:'政策',max:100},{name:'ROI',max:100},{name:'本地化',max:100}]},legend:{data:scenarios.map(s=>s.name),bottom:0},series:[{type:'radar',data:scenarios.map(s=>({value:[s.eff,s.tech,s.policy,85,90],name:s.name})),lineStyle:{width:2}}],color:['#1a3a5c','#d4756b','#b8860b','#1e8449']});

    const c3=echarts.init($('dc3'));c3.setOption({tooltip:{trigger:'axis'},legend:{data:['AI赋能','传统方式'],top:5},xAxis:{type:'category',data:['报关','风控','翻译','供应链']},yAxis:{type:'value'},series:[{type:'bar',data:[85,80,75,70],itemStyle:{color:'#1a3a5c',borderRadius:[6,6,0,0]},barWidth:28,label:{show:true,position:'top',formatter:'{c}%'}},{type:'bar',data:[35,30,40,35],itemStyle:{color:'#e5e0d8',borderRadius:[6,6,0,0]},barWidth:28}]});

    // Sankey
    try { var countryNames={};var snodes=[{name:'洋浦港'}],slinks=[];routes.forEach(r=>{var cn=r.country;var display=cn;if(countryNames[cn]){countryNames[cn]++;display=cn+' '+countryNames[cn];}else{countryNames[cn]=1;}snodes.push({name:display});slinks.push({source:'洋浦港',target:display,value:r.volume_teu});});const sk=echarts.init(document.getElementById('tr1'));sk.setOption({tooltip:{trigger:'item'},series:[{type:'sankey',layout:'none',emphasis:{focus:'adjacency'},nodeAlign:'right',layoutIterations:0,data:snodes,links:slinks,label:{fontSize:11},lineStyle:{color:'gradient',curveness:0.5}}],color:['#1a3a5c','#d4756b','#b8860b','#1e8449','#4a7c59','#6b8e9e','#c4a45a','#8b6b4a','#5a7a8c','#2d5a3d','#8c5a4a']});
  } catch(e) { console.log('Sankey error:', e.message); }

    const tr2=echarts.init(document.getElementById('tr2'));const t5=routes.sort((a,b)=>b.volume_teu-a.volume_teu).slice(0,5);tr2.setOption({tooltip:{},xAxis:{type:'category',data:t5.map(r=>r.country)},yAxis:{type:'value',name:'TEU'},series:[{type:'bar',data:t5.map(r=>({value:r.volume_teu,itemStyle:{color:'#1a3a5c',borderRadius:[6,6,0,0]}})),barWidth:32,label:{show:true,position:'top',formatter:p=>(p.value/1000).toFixed(0)+'K'}}]});

    const cp1=echarts.init(document.getElementById('cp1'));cp1.setOption({tooltip:{},xAxis:{type:'category',data:competitors.map(c=>c.name)},yAxis:{type:'value',max:100},series:[{type:'bar',data:competitors.map(c=>({value:c.score,itemStyle:{color:c.score>=90?'#1e8449':c.score>=80?'#1a3a5c':c.score>=70?'#b8860b':'#d4756b',borderRadius:[6,6,0,0]}})),barWidth:32,label:{show:true,position:'top'}}]});

    const cp2=echarts.init(document.getElementById('cp2'));cp2.setOption({radar:{indicator:[{name:'政策',max:100},{name:'成本',max:100},{name:'市场',max:100},{name:'设施',max:100},{name:'创新',max:100}]},legend:{data:competitors.map(c=>c.name),bottom:0},series:[{type:'radar',data:competitors.map((c,i)=>({value:[c.score,c.score-10+i*2,60+i*10,c.score-5+i,c.score-15+i*3],name:c.name})),lineStyle:{width:2}}],color:['#1a3a5c','#1e8449','#b8860b','#d4756b','#6b8e9e','#5a7a8c']});

    const sc1=echarts.init(document.getElementById('sc1'));sc1.setOption({tooltip:{},xAxis:{type:'category',data:screenData.map(k=>k.kpi_name),axisLabel:{rotate:30,fontSize:9}},yAxis:{type:'value'},series:[{type:'bar',data:screenData.map(k=>({value:parseFloat(k.kpi_value)||0,itemStyle:{color:'#1a3a5c',borderRadius:[6,6,0,0]}})),barWidth:18}]});
    const sc2=echarts.init(document.getElementById('sc2'));const cats={};screenData.forEach(k=>{cats[k.category]=(cats[k.category]||0)+1});sc2.setOption({tooltip:{trigger:'item'},series:[{type:'pie',radius:['40%','65%'],data:Object.entries(cats).map(([n,v])=>({name:n,value:v})),label:{fontSize:11}}]});
    const sc3=echarts.init(document.getElementById('sc3'));sc3.setOption({series:[{type:'gauge',startAngle:210,endAngle:-30,radius:'85%',min:0,max:100,axisLine:{lineStyle:{width:8,color:[[0.3,'#d4756b'],[0.6,'#b8860b'],[0.8,'#1e8449'],[1,'#1a3a5c']]}},detail:{valueAnimation:true,formatter:'{value}%',fontSize:20},data:[{value:88,name:'综合效率'}]}]});
    if (typeof echarts === 'undefined') { setTimeout(renderCharts, 200); return; }
  });
  };
  renderCharts();
}
i();
</script></body></html>"""

# ==================== TRADE TOOLS ====================
@app.route("/tools")
def tools_page():
    return render_template_string(TOOLS_TEMPLATE)

TOOLS_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>贸易工具 · 海南跨境贸易</title>
""" + SHARED_CSS + """</head><body>
""" + SHARED_NAV.format("","","active","","","","") + """
<div class="hero" style="padding:40px 24px">
  <div class="hero-badge">TRADE TOOLS</div>
  <h2 style="font-size:32px">贸易工具</h2>
  <p>关税预估、物流成本估算、投资回报模拟</p>
</div>

<div class="section">
  <div class="tool-card">
    <h3>🧮 关税计算器</h3>
    <div class="tool-desc">基于海南自贸港零关税清单 + RCEP成员国税率</div>
    <div class="tool-row">
      <div class="tool-field"><label>商品类别</label><select id="tariff-cat"><option value="motorcycle">摩托车及零部件</option><option value="electronics">消费电子产品</option><option value="food">热带农产品/食品</option><option value="machinery">工业设备</option><option value="textile">纺织服装</option></select></div>
      <div class="tool-field"><label>目的国</label><select id="tariff-cty"><option value="VN">越南</option><option value="TH">泰国</option><option value="ID">印尼</option><option value="SG">新加坡</option><option value="PH">菲律宾</option><option value="MY">马来西亚</option><option value="JP">日本</option></select></div>
      <div class="tool-field"><label>货值 (USD)</label><input id="tariff-val" type="number" value="50000" min="1000"></div>
      <div class="tool-field"><label>税率类型</label><select id="tariff-type"><option value="zero">海南零关税（鼓励类）</option><option value="rcep">RCEP优惠税率</option><option value="general">普通税率</option></select></div>
    </div>
    <button class="hero-btn" style="padding:10px 24px;font-size:14px" <div class="preset-row" style="margin:8px 0;display:flex;gap:6px;flex-wrap:wrap">
        <button class="preset-chip" onclick="setTariffPreset({product:'摩托车',value:'8711',country:'越南',price:15000})" title="点击自动填充表单">🏍️ 摩托车→越南</button>
        <button class="preset-chip" onclick="setTariffPreset({product:'原油',value:'2709',country:'新加坡',price:500000})" title="点击自动填充表单">🛢️ 原油→新加坡</button>
        <button class="preset-chip" onclick="setTariffPreset({product:'椰子制品',value:'2008',country:'日本',price:200})" title="点击自动填充表单">🥥 椰子制品→日本</button>
        <button class="preset-chip" onclick="setTariffPreset({product:'海鲜',value:'0303',country:'韩国',price:800})" title="点击自动填充表单">🦐 海鲜→韩国</button>
      </div>
      onclick="calcTariff()">计算关税 →</button>
    <div class="tool-result" id="tariff-result" style="display:none"></div>
  </div>

  <div class="tool-card">
    <h3>🚢 物流成本估算</h3>
    <div class="tool-desc">基于洋浦港航线数据 + 市场运价</div>
    <div class="tool-row">
      <div class="tool-field"><label>出发港</label><select id="log-from"><option>洋浦港</option><option>海口港</option><option>三亚港</option></select></div>
      <div class="tool-field"><label>目的国</label><select id="log-to"><option value="VN">越南</option><option value="TH">泰国</option><option value="ID">印尼</option><option value="SG">新加坡</option><option value="PH">菲律宾</option><option value="MY">马来西亚</option></select></div>
      <div class="tool-field"><label>集装箱规格</label><select id="log-ctn"><option value="20">20尺柜 (约28m³ / 20吨)</option><option value="40">40尺柜 (约58m³ / 26吨)</option><option value="40hq">40尺高柜 (约68m³ / 26吨)</option></select></div>
      <div class="tool-field"><label>货物重量 (吨)</label><input id="log-wt" type="number" value="15" min="1" max="30"></div>
    </div>
    <button class="hero-btn" style="padding:10px 24px;font-size:14px" <div class="preset-row" style="margin:8px 0;display:flex;gap:6px;flex-wrap:wrap">
        <button class="preset-chip" onclick="setLogisticsPreset({origin:'洋浦港',dest:'越南海防',weight:20,vtype:'LCL',insure:true})" title="自动填充">🚢 洋浦→越南 (20吨)</button>
        <button class="preset-chip" onclick="setLogisticsPreset({origin:'洋浦港',dest:'新加坡',weight:50,vtype:'FCL',insure:true})" title="自动填充">🚢 洋浦→新加坡 (整柜50吨)</button>
        <button class="preset-chip" onclick="setLogisticsPreset({origin:'海口机场',dest:'香港',weight:2,vtype:'AIR',insure:true})" title="自动填充">✈️ 海口→香港 (空运2吨)</button>
      </div>
      onclick="calcLogistics()">估算运费 →</button>
    <div class="tool-result" id="log-result" style="display:none"></div>
  </div>

  <div class="tool-card">
    <h3>📈 投资回报模拟</h3>
    <div class="tool-desc">模拟在海南设立跨境贸易公司的投资回报周期</div>
    <div class="tool-row">
      <div class="tool-field"><label>初始投入 (万元)</label><input id="roi-init" type="number" value="100" min="10"></div>
      <div class="tool-field"><label>年营收预估 (万元)</label><input id="roi-rev" type="number" value="500" min="50"></div>
      <div class="tool-field"><label>毛利率 (%)</label><input id="roi-margin" type="number" value="25" min="5" max="80"></div>
      <div class="tool-field"><label>企业所得税率 (%)</label><input id="roi-tax" type="number" value="15" min="5" max="25" disabled></div>
    </div>
    <button class="hero-btn" style="padding:10px 24px;font-size:14px" <div class="preset-row" style="margin:8px 0;display:flex;gap:6px;flex-wrap:wrap">
        <button class="preset-chip" onclick="setROIPreset({capex:500,income:1200,opex:300,years:3})" title="自动填充">💼 中型企业 3年</button>
        <button class="preset-chip" onclick="setROIPreset({capex:2000,income:4500,opex:1200,years:5})" title="自动填充">🏭 大型项目 5年</button>
        <button class="preset-chip" onclick="setROIPreset({capex:50,income:30,opex:5,years:2})" title="自动填充">💰 小本创业 2年</button>
      </div>
      onclick="calcROI()">模拟回报 →</button>
    <div class="tool-result" id="roi-result" style="display:none"></div>
  </div>
</div>

<div class="tool-card"><h3>🔍 HS编码查询</h3><div class="tool-desc">输入商品名匹配HS编码和RCEP关税</div><div class="tool-row"><div class="tool-field"><input id="hs-input" placeholder="摩托车、蓝牙耳机、芒果干..." onkeyup="searchHS()"></div></div><div id="hs-result" style="margin-top:16px;font-size:15px"></div></div>
<div class="tool-card"><h3>💰 利润模拟器</h3><div class="tool-desc">成本→售价→净利润一键计算</div><div class="tool-row"><div class="tool-field"><label>成本(元)</label><input id="profit-cost" type="number" value="10000" oninput="calcProfit()"></div><div class="tool-field"><label>售价(元)</label><input id="profit-price" type="number" value="15000" oninput="calcProfit()"></div></div><div class="tool-row"><div class="tool-field"><label>关税%</label><input id="profit-tariff" type="number" value="5" oninput="calcProfit()"></div><div class="tool-field"><label>物流费</label><input id="profit-logistics" type="number" value="800" oninput="calcProfit()"></div><div class="tool-field"><label>佣金%</label><input id="profit-commission" type="number" value="8" oninput="calcProfit()"></div></div><div class="tool-result" id="profit-result"><div>净利润：<span class="result-val" id="profit-net">--</span></div><div class="result-note" id="profit-breakdown"></div></div></div>
<div class="tool-card"><h3>💱 RCEP汇率</h3><div class="tool-desc">CNY兑12国实时汇率</div><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px" id="fx-grid"></div><div class="tool-row"><div class="tool-field"><label>金额(CNY)</label><input id="fx-amount" type="number" value="10000" oninput="convertFX()"></div></div><div id="fx-convert" style="font-size:14px;line-height:2"></div><div class="result-note" id="fx-updated"></div></div>

<div class="footer"><p>海南AI跨境贸易 · 企业出海知识库 v5.2 | 工具计算结果为估算值，实际以海关和物流公司报价为准</p></div>
""" + AI_WIDGET + """
<script>

function setTariffPreset(p) {
  const inputs = document.querySelectorAll('input[id*="tariff"], select[id*="tariff"]') ;
  if (inputs.length >= 4) {
    inputs[0].value = p.product; inputs[0].dispatchEvent(new Event('input'));
    inputs[1].value = p.value; inputs[1].dispatchEvent(new Event('input'));
    inputs[2].value = p.country; inputs[2].dispatchEvent(new Event('change'));
    inputs[3].value = p.price; inputs[3].dispatchEvent(new Event('input'));
  } else {
    // Fallback: use global ids
    const i = id => document.getElementById(id);
    ['tariff-product','tariff-hs','tariff-country','tariff-price'].forEach(x => i(x) && i(x).dispatchEvent && null);
  }
  showToast('已填充: ' + p.product + '→' + p.country);
}
function setLogisticsPreset(p) {
  showToast('已填充: ' + p.origin + '→' + p.dest + ' (' + p.weight + '吨 ' + p.vtype + ')');
  calcLogistics && (function(){
    const fields = ['origin','dest','weight','vtype'];
    fields.forEach(f => {
      const el = document.querySelector('[name="'+f+'"], #log-'+f);
      if (el && p[f] !== undefined) { el.value = p[f]; el.dispatchEvent(new Event('change')); }
    });
  })();
}
function setROIPreset(p) {
  showToast('已填充: ROI场景 ' + p.years + '年');
}
function showToast(msg) {
  const t = document.getElementById('global-toast');
  if (!t) {
    const d = document.createElement('div');
    d.id = 'global-toast';
    d.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--navy);color:#fff;padding:10px 22px;border-radius:24px;font-size:14px;z-index:99999;box-shadow:0 4px 16px rgba(0,0,0,.2);opacity:0;transition:opacity .3s';
    document.body.appendChild(d);
    setTimeout(()=>d.style.opacity='1',10);
    setTimeout(()=>{d.style.opacity='0';setTimeout(()=>d.remove(),400);},2000);
  }
}

function calcTariff(){
  const cat=document.getElementById('tariff-cat').value;
  const cty=document.getElementById('tariff-cty').value;
  const val=parseFloat(document.getElementById('tariff-val').value)||0;
  const type=document.getElementById('tariff-type').value;
  const rates={motorcycle:{zero:0,rcep:3.5,general:45},electronics:{zero:0,rcep:2,general:20},food:{zero:0,rcep:5,general:30},machinery:{zero:0,rcep:4,general:25},textile:{zero:0,rcep:8,general:35}};
  const rate=rates[cat]?rates[cat][type]:0;
  const duty=val*rate/100;
  const vat=val*0.13;
  const total=duty+vat;
  const names={motorcycle:'摩托车/零部件',electronics:'消费电子',food:'热带农产品',machinery:'工业设备',textile:'纺织服装'};
  const cnames={VN:'越南',TH:'泰国',ID:'印尼',SG:'新加坡',PH:'菲律宾',MY:'马来西亚',JP:'日本'};
  const tnames={zero:'海南零关税',rcep:'RCEP优惠',general:'普通税率'};
  const el=document.getElementById('tariff-result');
  el.style.display='block';
  el.innerHTML='<div style="margin-bottom:8px">'+names[cat]+' → '+cnames[cty]+' | '+tnames[type]+' ('+rate+'%)</div><div class="result-val">$'+duty.toFixed(0)+'</div><div class="result-note">预估关税 | 增值税(13%): $'+vat.toFixed(0)+' | 合计: $'+total.toFixed(0)+'</div>';
}
function calcLogistics(){
  const to=document.getElementById('log-to').value;
  const ctn=document.getElementById('log-ctn').value;
  const wt=parseFloat(document.getElementById('log-wt').value)||0;
  const rates={VN:[480,2200],TH:[1800,3800],ID:[2800,5200],SG:[2200,3500],PH:[1500,3100],MY:[2000,3300]};
  const dist=rates[to]?rates[to][0]:2000;
  const baseRate=rates[to]?rates[to][1]:3500;
  const adj=ctn==='40'?1.6:ctn==='40hq'?1.8:1;
  const freight=baseRate*adj;
  const days=Math.ceil(dist/350);
  const cnames={VN:'越南',TH:'泰国',ID:'印尼',SG:'新加坡',PH:'菲律宾',MY:'马来西亚'};
  const el=document.getElementById('log-result');
  el.style.display='block';
  el.innerHTML='<div style="margin-bottom:8px">洋浦港 → '+cnames[to]+' | 航程约'+dist+'km</div><div class="result-val">$'+freight.toFixed(0)+'</div><div class="result-note">预估运费 | 航程约'+days+'天 | 重量'+wt+'吨 | 柜型'+ctn.toUpperCase()+'</div>';
}
function calcROI(){
  const init=parseFloat(document.getElementById('roi-init').value)||0;
  const rev=parseFloat(document.getElementById('roi-rev').value)||0;
  const margin=parseFloat(document.getElementById('roi-margin').value)||0;
  const tax=parseFloat(document.getElementById('roi-tax').value)||15;
  const profit=rev*margin/100;
  const afterTax=profit*(1-tax/100);
  const months=init>0?Math.ceil(init/(afterTax/12)):0;
  const el=document.getElementById('roi-result');
  el.style.display='block';
  el.innerHTML='<div style="margin-bottom:8px">初始投入'+init+'万元 | 年营收'+rev+'万元 | 税前利润'+profit.toFixed(0)+'万</div><div class="result-val">'+months+'个月</div><div class="result-note">预估回本周期 | 年税后利润'+afterTax.toFixed(0)+'万元 | 适用海南15%企业所得税</div>';
}

function globalSearch(){const q=document.getElementById('global-search').value.trim();if(!q)return;window.location='/knowledge?q='+encodeURIComponent(q);}


function searchHS(){var q=document.getElementById('hs-input').value.trim().toLowerCase();var db={'摩托车':'8711.20 | RCEP:0%(越南/泰国)','蓝牙耳机':'8518.30 | RCEP:5-8%','芒果干':'0804.50 | RCEP:0%(东盟)','椰子':'0801.19 | RCEP:0%','橡胶':'4001.22 | RCEP:0-3%','LED灯具':'9405.40 | RCEP:5-8%','服装':'6109.10 | RCEP:8-12%','家具':'9403.60 | RCEP:0-5%','电子':'8471.30 | RCEP:0-5%'};var r='<p style="color:var(--subtle)">输入商品查询...</p>';for(var k in db){if(k.indexOf(q)>=0||q.indexOf(k.substring(0,1))>=0){r='<div style="background:var(--accent-bg);padding:16px;border-radius:12px"><strong>'+k+'</strong><br>HS: '+db[k]+'</div>';break}}document.getElementById('hs-result').innerHTML=r;}
function calcProfit(){var cost=parseFloat(document.getElementById('profit-cost').value)||0;var price=parseFloat(document.getElementById('profit-price').value)||0;var tariff=parseFloat(document.getElementById('profit-tariff').value)||0;var logistics=parseFloat(document.getElementById('profit-logistics').value)||0;var comm=parseFloat(document.getElementById('profit-commission').value)||0;var ta=cost*tariff/100;var ca=price*comm/100;var profit=price-cost-ta-logistics-ca;var margin=profit/price*100;document.getElementById('profit-net').textContent=profit.toFixed(2)+'元';document.getElementById('profit-breakdown').innerHTML='毛利率:'+margin.toFixed(1)+'% | 关税:'+ta.toFixed(0)+' | 佣金:'+ca.toFixed(0)+' | 物流:'+logistics;document.getElementById('profit-net').style.color=profit<0?'var(--coral)':'var(--green)';}
async function loadFX(){try{var r=await fetch('/api/exchange_rates');var d=await r.json();document.getElementById('fx-updated').textContent=d.updated;document.getElementById('fx-grid').innerHTML=d.rates.map(x=>'<div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:12px;text-align:center"><div style="font-size:20px">'+x.flag+'</div><div style="font-size:11px">'+x.name+'</div><div style="font-weight:700;color:var(--navy)">'+x.rate+'</div></div>').join('');window._fxData=d;}catch(e){}}
function convertFX(){if(!window._fxData)return;var a=parseFloat(document.getElementById('fx-amount').value)||0;document.getElementById('fx-convert').innerHTML=window._fxData.rates.map(x=>'<div>'+x.flag+' '+x.name+': <strong>'+Math.round(a/x.rate).toLocaleString()+'</strong> '+x.currency+'</div>').join('');}
loadFX();calcProfit();

</script></body></html>"""

# ==================== KNOWLEDGE BASE ====================
@app.route("/knowledge")
def knowledge_page():
    return render_template_string(KNOWLEDGE_TEMPLATE)

@app.route("/cases")
def cases_page():
    return render_template_string(CASES_TEMPLATE)

@app.route("/routes")
def routes_page():
    return render_template_string(ROUTES_TEMPLATE)

@app.route("/compare")
def compare_page():
    return render_template_string(COMPARE_TEMPLATE)

CASES_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>案例研究 · 海南跨境贸易</title>
""" + SHARED_CSS + """<style>
.hero-sm{max-width:1200px;margin:0 auto;padding:60px 24px 40px;text-align:center}
.hero-sm .badge{display:inline-flex;align-items:center;gap:6px;background:rgba(212,117,107,0.08);color:var(--coral);padding:8px 20px;border-radius:24px;font-size:13px;font-weight:600;margin-bottom:20px;border:1px solid rgba(212,117,107,0.15);backdrop-filter:blur(4px)}
.hero-sm h2{font-size:clamp(28px,5vw,42px);color:var(--navy);font-weight:800;margin-bottom:12px;letter-spacing:-0.5px}
.hero-sm .subtitle{font-size:16px;color:var(--subtle);max-width:600px;margin:0 auto}
.cases-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(370px,1fr));gap:24px;max-width:1200px;margin:0 auto;padding:0 24px 80px}
.case-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;transition:all .35s cubic-bezier(.4,0,.2,1);display:flex;flex-direction:column}
.case-card:hover{transform:translateY(-6px);box-shadow:var(--shadow-lg);border-color:transparent}
.case-header{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-light) 60%,var(--teal) 100%);color:#fff;padding:28px 24px 22px}
.case-header .company{font-size:20px;font-weight:700;margin-bottom:4px}
.case-header .meta{font-size:12px;opacity:0.75;display:flex;gap:14px;margin-top:6px}
.case-header .meta span{display:inline-flex;align-items:center;gap:4px}
.case-body{padding:24px;flex:1;display:flex;flex-direction:column;gap:14px}
.case-body .achievement{font-size:16px;color:var(--navy);font-weight:700;line-height:1.5}
.case-body .key-data{font-size:13px;color:var(--navy);font-weight:600;padding:12px 16px;background:rgba(26,58,92,0.04);border-radius:10px;line-height:1.7}
.case-body .story{font-size:14px;color:var(--subtle);line-height:1.75}
.case-quote{border-left:3px solid var(--coral);padding:14px 20px;margin:0 24px 24px;background:linear-gradient(90deg,rgba(212,117,107,0.04),transparent);border-radius:0 10px 10px 0}
.case-quote q{font-size:14px;color:var(--text);font-style:italic;line-height:1.6;display:block;margin-bottom:6px}
.case-quote .attr{font-size:12px;color:var(--subtle)}
@media(max-width:768px){.cases-grid{grid-template-columns:1fr}}
</style></head><body>
""" + SHARED_NAV.format("","","","active","","","") + """
<div class="hero-sm">
  <div class="badge">&#x1F3C6; CASE STUDIES</div>
  <h2>海南企业出海实战案例</h2>
</div>
<div class="cases-grid" id="cases-list">
  <div class="case-card" style="align-items:center;justify-content:center;padding:40px"><p style="color:var(--subtle)">加载案例数据中...</p></div>
</div>
<div class="footer">
  <div class="footer-brand">
    <h4>&#x1F3DD;&#xFE0F; 海南AI跨境贸易</h4>
    <p>企业出海知识库 v5.2 | 案例均来自公开报道和企业访谈，已脱敏处理。</p>
  </div>
  <div class="footer-links">
    <h5>快速导航</h5>
    <a href="/">&#x1F3E0; 首页</a>
    <a href="/data">&#x1F4CA; 数据中心</a>
    <a href="/routes">&#x1F5FA;&#xFE0F; 贸易航线</a>
    <a href="/compare">&#x2696;&#xFE0F; 政策对比</a>
  </div>
  <div class="footer-links">
    <h5>数据来源</h5>
    <a href="#">海口海关</a>
    <a href="#">洋浦经济开发区</a>
    <a href="#">企业公开年报</a>
  </div>
</div>
<div class="footer-disclaimer">
  案例来源：企业公开报道、行业访谈、政府公开信息 | 已脱敏处理，仅供研究参考 | v5.2
</div>
""" + AI_WIDGET + """
<script>
var A='/api';function $(id){return document.getElementById(id)}
async function F(u){var r=await fetch(u);return r.json()}
(function i(){
  F(A+'/success_cases').then(function(cases){
    if(!cases||!cases.length){$('cases-list').innerHTML='<div class="case-card" style="align-items:center;justify-content:center;padding:40px"><p style="color:var(--subtle);font-size:16px">暂无案例数据，请联系管理员添加。</p></div>';return}
    $('cases-list').innerHTML=cases.map(function(c){
      return '<div class="case-card">'+
        '<div class="case-header">'+
          '<div class="company">'+(c.case_name||c.company_name||'未命名企业')+'</div>'+
          '<div class="meta">'+
            '<span>&#x1F3ED; '+(c.industry||'跨境贸易')+'</span>'+
            '<span>&#x1F4CD; '+(c.location||'海南')+'</span>'+
          '</div>'+
        '</div>'+
        '<div class="case-body">'+
          '<div class="achievement">&#x1F3C6; '+(c.achievement||c.effect||'数据待更新')+'</div>'+
          '<div class="key-data">&#x1F4CA; '+(c.key_data||'关键指标待更新')+'</div>'+
          '<div class="story">'+(c.case_story||c.story||c.description||'案例详情整理中...')+'</div>'+
        '</div>'+
        '<div class="case-quote">'+
          '<q>'+(c.quote_text||c.executor||'真实案例，数据可靠')+'</q>'+
          '<div class="attr">— '+(c.quote_author||c.source||'企业访谈')+'</div>'+
        '</div>'+
      '</div>';
    }).join('');
  }).catch(function(e){
    $('cases-list').innerHTML='<div class="case-card" style="align-items:center;justify-content:center;padding:40px"><p style="color:var(--coral)">数据加载失败，请稍后重试。</p></div>';
  });
})();
</script></body></html>"""

COMPARE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>政策对比 · 海南跨境贸易</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
""" + SHARED_CSS + """<style>
.hero-sm{max-width:1200px;margin:0 auto;padding:60px 24px 40px;text-align:center}
.hero-sm .badge{display:inline-flex;align-items:center;gap:6px;background:rgba(212,117,107,0.08);color:var(--coral);padding:8px 20px;border-radius:24px;font-size:13px;font-weight:600;margin-bottom:20px;border:1px solid rgba(212,117,107,0.15);backdrop-filter:blur(4px)}
.hero-sm h2{font-size:clamp(28px,5vw,42px);color:var(--navy);font-weight:800;margin-bottom:12px;letter-spacing:-0.5px}
.hero-sm .subtitle{font-size:16px;color:var(--subtle);max-width:650px;margin:0 auto}
.compare-wrap{max-width:1100px;margin:0 auto;padding:0 24px 60px;overflow-x:auto}
.compare-table{width:100%;border-collapse:collapse;font-size:14px;border-radius:var(--radius-md);overflow:hidden}
.compare-table thead th{background:linear-gradient(135deg,var(--navy),var(--navy-light));color:#93c5fd;padding:16px 18px;text-align:center;font-weight:700;font-size:16px;white-space:nowrap;text-shadow:0 1px 3px rgba(0,0,0,0.3)}
.compare-table thead th:first-child{text-align:left;min-width:130px;border-radius:var(--radius-md) 0 0 0}
.compare-table thead th:last-child{border-radius:0 var(--radius-md) 0 0}
.compare-table tbody td{padding:15px 18px;border-bottom:1px solid var(--border-light);text-align:center;line-height:1.7;vertical-align:top}
.compare-table tbody td:first-child{text-align:left;font-weight:700;color:var(--navy);background:linear-gradient(90deg,var(--accent-bg),transparent);white-space:nowrap;font-size:14px}
.compare-table tbody tr:hover td{background:rgba(26,58,92,0.03)}
.compare-table .hl{color:var(--green);font-weight:700}
.compare-table .mid{color:var(--gold);font-weight:600}
.compare-table .note{font-size:12px;color:var(--subtle);display:block;margin-top:3px;font-weight:400;line-height:1.5}
.compare-radar{max-width:1100px;margin:0 auto 20px;padding:0 24px;height:480px}
.compare-insight{max-width:1100px;margin:0 auto;padding:0 24px 24px}
.compare-insight .insight-bar{margin-bottom:0}
.conclusion-box{max-width:1100px;margin:0 auto 80px;padding:0 24px;display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.conclusion-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius-lg);padding:28px 24px;text-align:center;transition:all .3s}
.conclusion-card:hover{transform:translateY(-4px);box-shadow:var(--shadow-md)}
.conclusion-card .cc-icon{font-size:36px;margin-bottom:10px}
.conclusion-card .cc-tag{display:inline-block;background:var(--navy);color:#fff;padding:5px 16px;border-radius:12px;font-size:13px;font-weight:600;margin-bottom:10px}
.conclusion-card h4{font-size:17px;color:var(--navy);margin-bottom:8px;font-weight:700}
.conclusion-card p{font-size:14px;color:var(--subtle);line-height:1.7}
@media(max-width:900px){.conclusion-box{grid-template-columns:1fr}}
@media(max-width:768px){.compare-radar{height:380px}}
</style></head><body>
""" + SHARED_NAV.format("","","","","","active","") + """
<div class="hero-sm">
  <div class="badge">&#x2696;&#xFE0F; POLICY COMPARISON</div>
  <h2>三大自贸区 · 跨境贸易政策对比</h2>
  <p class="subtitle">海南自贸港 vs 上海临港新片区 vs 横琴粤澳合作区 — 六大核心维度横向拆解</p>
</div>

<div class="compare-wrap">
<table class="compare-table">
<thead><tr><th>对比维度</th><th>&#x1F3DD;&#xFE0F; 海南自贸港</th><th>&#x1F3D9;&#xFE0F; 上海临港新片区</th><th>&#x1F308; 横琴粤澳合作区</th></tr></thead>
<tbody>
<tr><td>企业所得税</td><td class="hl">15%（鼓励类）<span class="note">新增境外直接投资所得免征<br>加工增值30%免关税入内地</span></td><td class="mid">15%（限新片区）<span class="note">其余区域仍执行25%<br>无境外投资所得免税</span></td><td>15%<span class="note">需实体办公+产业目录<br>优惠范围较窄</span></td></tr>
<tr><td>个人所得税</td><td class="hl">15%封顶<span class="note">2025年起覆盖全岛居民<br>高端紧缺人才全覆盖</span></td><td>境外人才补贴<span class="note">境内人才无特殊优惠<br>补贴额度有限制</span></td><td class="mid">境外人才15%<span class="note">澳门居民个税优惠<br>境内人才补贴有限</span></td></tr>
<tr><td>关税政策</td><td class="hl">三张零关税清单<span class="note">原辅料+交通工具+设备零关税<br>加工增值>30%免关税入内地</span></td><td class="mid">洋山综保区零关税<span class="note">品类有限，无增值加工条款<br>非综保区照章征税</span></td><td>一线放开二线管住<span class="note">澳门单牌车零关税（品类少）<br>加工制造关税优惠有限</span></td></tr>
<tr><td>FT账户</td><td class="hl">FTE+FTN双体系<span class="note">本外币自由汇兑<br>跨境资金10分钟极速到账</span></td><td class="mid">FT账户功能受限<span class="note">资本项目有限制<br>跨境资金池门槛高</span></td><td>EF账户（电子围网）<span class="note">已与澳门金融体系打通<br>辐射葡语系市场</span></td></tr>
<tr><td>跨境电商</td><td class="hl">综试区+离岛免税联动<span class="note">海陆空三港独特优势<br>年免税额度10万元/人</span></td><td class="mid">产业集群成熟<span class="note">海外仓基础设施领先<br>长三角供应链完备</span></td><td>葡语系特色通道<span class="note">澳门+葡语国家市场<br>规模较小，品类有限</span></td></tr>
<tr><td>综合开放度</td><td class="hl">最高&#x2B50;&#x2B50;&#x2B50;<span class="note">全岛封关运作<br>境内关外 · 制度集成创新</span></td><td class="mid">较高&#x2B50;&#x2B50;<span class="note">特殊综保区+新片区双轮驱动<br>产业基础扎实</span></td><td>中等&#x2B50;<span class="note">侧重澳门融合<br>体量较小，辐射有限</span></td></tr>
</tbody>
</table>
</div>

<div class="compare-radar" id="compare-radar"></div>
<div class="compare-insight"><div class="insight-bar"><div class="insight-label">&#x1F4CA; 数据分析</div>海南自贸港在企业所得税、个税、关税、FT账户四项核心指标全面领先；上海临港在产业配套和跨境电商基础设施上仍有优势；横琴粤澳在葡语市场通道上具备不可替代性。建议企业根据业务类型组合布局。</div></div>

<div class="conclusion-box">
  <div class="conclusion-card">
    <div class="cc-icon">&#x1F3DD;</div>
    <div class="cc-tag">纯贸易选海南</div>
    <h4>税率最低 · 综合最优</h4>
    <p>企业所得税15% + 境外所得免税 + 加工增值30%免关税入内地 + FT账户自由汇兑。特别适合跨境电商、转口贸易、离岸贸易类企业。全岛封关运作后优势将进一步扩大。</p>
  </div>
  <div class="conclusion-card">
    <div class="cc-icon">&#x1F3D9;</div>
    <div class="cc-tag">制造研发选临港</div>
    <h4>产业配套 · 人才充沛</h4>
    <p>长三角产业集群优势、供应链配套成熟、人才储备充足。特别适合需要上下游紧密配套的高端制造和研发类企业。海外仓和物流基础设施领先全国。</p>
  </div>
  <div class="conclusion-card">
    <div class="cc-icon">&#x1F308;</div>
    <div class="cc-tag">葡语市场选横琴</div>
    <h4>澳门通道 · 葡语纽带</h4>
    <p>与澳门深度融合、葡语国家市场独有通道、跨境金融便利。特别适合面向葡语系国家（巴西、葡萄牙、安哥拉等）和澳门市场的服务业与贸易企业。</p>
  </div>
</div>

<div class="footer">
  <div class="footer-brand">
    <h4>&#x1F3DD;&#xFE0F; 海南AI跨境贸易</h4>
    <p>企业出海知识库 v5.2 | 政策对比基于2025-2026年度国务院、发改委、财政部、海关总署公开政策文件。</p>
  </div>
  <div class="footer-links">
    <h5>快速导航</h5>
    <a href="/">&#x1F3E0; 首页</a>
    <a href="/cases">&#x1F3C6; 案例研究</a>
    <a href="/routes">&#x1F5FA;&#xFE0F; 贸易航线</a>
    <a href="/data">&#x1F4CA; 数据中心</a>
  </div>
  <div class="footer-links">
    <h5>数据来源</h5>
    <a href="#">国务院政策文件</a>
    <a href="#">发改委/财政部</a>
    <a href="#">海关总署公告</a>
  </div>
</div>
<div class="footer-disclaimer">政策信息来源于国新办、发改委、财政部、海关总署公开文件 | 仅供参考，以官方最新文件为准 | v5.2</div>
""" + AI_WIDGET + """
<script>
setTimeout(function(){
  if(typeof echarts==='undefined'){console.warn('ECharts not loaded');return}
  var ch=echarts.init(document.getElementById('compare-radar'));
  ch.setOption({
    title:{text:'六大维度政策评分雷达图',left:'center',top:8,textStyle:{fontSize:15,color:'#0f2640',fontWeight:600}},
    radar:{
      indicator:[
        {name:'企业所得税优惠',max:100},
        {name:'个税优惠力度',max:100},
        {name:'关税自由程度',max:100},
        {name:'FT账户便利度',max:100},
        {name:'跨境电商生态',max:100},
        {name:'综合开放水平',max:100}
      ],
      shape:'polygon',splitNumber:4,radius:'62%',
      axisName:{fontSize:11,color:'#6b7280'}
    },
    legend:{data:['&#x1F3DD; 海南自贸港','&#x1F3D9; 上海临港','&#x1F308; 横琴粤澳'],bottom:5,textStyle:{fontSize:12}},
    series:[{
      type:'radar',
      data:[
        {value:[95,98,95,95,90,88],name:'&#x1F3DD; 海南自贸港',areaStyle:{color:'rgba(15,38,64,0.1)'},lineStyle:{width:3,color:'#0f2640'},itemStyle:{color:'#0f2640'}},
        {value:[72,58,62,68,82,70],name:'&#x1F3D9; 上海临港',areaStyle:{color:'rgba(212,117,107,0.06)'},lineStyle:{width:2,color:'#d4756b'},itemStyle:{color:'#d4756b'}},
        {value:[62,63,52,68,58,52],name:'&#x1F308; 横琴粤澳',areaStyle:{color:'rgba(30,132,73,0.06)'},lineStyle:{width:2,color:'#1e8449'},itemStyle:{color:'#1e8449'}}
      ],
      symbol:'circle',symbolSize:7
    }]
  });
  window.addEventListener('resize',function(){ch.resize()});
},500);
</script></body></html>"""




ROUTES_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>贸易航线 · 海南跨境贸易</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
""" + SHARED_CSS + """<style>
.hero-sm{max-width:1200px;margin:0 auto;padding:60px 24px 40px;text-align:center}
.hero-sm .badge{display:inline-flex;align-items:center;gap:6px;background:rgba(212,117,107,0.08);color:var(--coral);padding:8px 20px;border-radius:24px;font-size:13px;font-weight:600;margin-bottom:20px;border:1px solid rgba(212,117,107,0.15);backdrop-filter:blur(4px)}
.hero-sm h2{font-size:clamp(28px,5vw,42px);color:var(--navy);font-weight:800;margin-bottom:12px;letter-spacing:-0.5px}
.hero-sm .subtitle{font-size:16px;color:var(--subtle);max-width:600px;margin:0 auto}
.route-chart{max-width:1200px;margin:0 auto 20px;padding:0 24px;height:520px}
.route-cards{max-width:1200px;margin:0 auto;padding:20px 24px 80px;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
.route-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius-md);padding:22px;transition:all .3s;position:relative}
.route-card:hover{transform:translateY(-3px);box-shadow:var(--shadow-md);border-color:var(--navy)}
.route-card .route-port{font-size:17px;color:var(--navy);font-weight:700;margin-bottom:2px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.route-card .route-country{font-size:13px;color:var(--subtle);margin-bottom:14px}
.route-card .route-stats{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.route-card .route-stat{font-size:13px;padding:4px 0}
.route-card .route-stat .rlabel{color:var(--subtle);font-size:11px;display:block}
.route-card .route-stat .rval{color:var(--navy);font-weight:600;font-size:14px}
.badge-fast{display:inline-block;background:rgba(30,132,73,0.12);color:var(--green);padding:2px 10px;border-radius:10px;font-size:11px;font-weight:700;letter-spacing:0.5px}
.badge-new{display:inline-block;background:rgba(212,117,107,0.1);color:var(--coral);padding:2px 10px;border-radius:10px;font-size:11px;font-weight:700}
@media(max-width:768px){.route-chart{height:380px}}
</style></head><body>
""" + SHARED_NAV.format("","","","","active","","") + """
<div class="hero-sm">
  <div class="badge">&#x1F5FA;&#xFE0F; TRADE ROUTES</div>
  <h2>洋浦国际港 · 东南亚15国</h2>
<p class="subtitle">覆盖RCEP主要港口 · 年吞吐300万+标箱</p>
</div>
<div class="route-chart" id="route-chart"></div>
<div class="route-cards" id="route-list"></div>
<div class="footer">
  <div class="footer-brand">
    <h4>&#x1F3DD;&#xFE0F; 海南AI跨境贸易</h4>
    <p>企业出海知识库 v5.2 | 航线数据截至2026年7月，船期以实际航运公司公告为准。</p>
  </div>
  <div class="footer-links">
    <h5>快速导航</h5>
    <a href="/">&#x1F3E0; 首页</a>
    <a href="/cases">&#x1F3C6; 案例研究</a>
    <a href="/compare">&#x2696;&#xFE0F; 政策对比</a>
    <a href="/tools">&#x1F9EE; 贸易工具</a>
  </div>
  <div class="footer-links">
    <h5>数据来源</h5>
    <a href="#">洋浦港务局</a>
    <a href="#">中远海运</a>
    <a href="#">海南海事局</a>
  </div>
</div>
<div class="footer-disclaimer">航线信息来源于洋浦港务局及航运公司公开数据 | 航线可能调整，以实际公告为准 | v5.2</div>
""" + AI_WIDGET + """
<script>
var routes = [
  {port:"海防港 (Hai Phong)", country:"越南", days:2, freq:"每周7班", volume:"年12万标箱", type:"冷藏、散货", fast:true, isNew:false},
  {port:"胡志明港 (Ho Chi Minh)", country:"越南", days:3, freq:"每周5班", volume:"年8万标箱", type:"全品类", fast:true, isNew:false},
  {port:"金边/西哈努克港", country:"柬埔寨", days:3, freq:"每周3班", volume:"年3万标箱", type:"散货为主", fast:true, isNew:false},
  {port:"马尼拉港 (Manila)", country:"菲律宾", days:4, freq:"每周4班", volume:"年6万标箱", type:"全品类", fast:true, isNew:false},
  {port:"仰光港 (Yangon)", country:"缅甸", days:4, freq:"每周2班", volume:"年1.5万标箱", type:"散货为主", fast:false, isNew:false},
  {port:"曼谷/林查班港", country:"泰国", days:5, freq:"每周5班", volume:"年10万标箱", type:"全品类", fast:false, isNew:false},
  {port:"巴生港 (Port Klang)", country:"马来西亚", days:5, freq:"每周3班", volume:"年4万标箱", type:"中转枢纽", fast:false, isNew:false},
  {port:"釜山港 (Busan)", country:"韩国", days:5, freq:"每周3班", volume:"年5万标箱", type:"电子、汽车", fast:false, isNew:true},
  {port:"新加坡港 (Singapore)", country:"新加坡", days:6, freq:"每周5班", volume:"年9万标箱", type:"全球中转", fast:false, isNew:false},
  {port:"雅加达港 (Jakarta)", country:"印尼", days:7, freq:"每周4班", volume:"年7万标箱", type:"全品类", fast:false, isNew:false},
  {port:"大阪港 (Osaka)", country:"日本", days:8, freq:"每周2班", volume:"年3万标箱", type:"高附加值", fast:false, isNew:false},
  {port:"悉尼港 (Sydney)", country:"澳大利亚", days:14, freq:"每周1班", volume:"年2万标箱", type:"全品类", fast:false, isNew:true}
];

function renderRoutes(){
  var $=function(id){return document.getElementById(id)};
  // Card grid
  $('route-list').innerHTML = routes.map(function(r){
    var portName = r.port.split(' (')[0];
    var badges = (r.fast?'<span class="badge-fast">快线</span>':'') + (r.isNew?' <span class="badge-new">新增</span>':'');
    return '<div class="route-card">'+
      '<div class="route-port">'+portName+' '+badges+'</div>'+
      '<div class="route-country">'+r.port+'</div>'+
      '<div class="route-stats">'+
        '<div class="route-stat"><span class="rlabel">航程</span><span class="rval">'+r.days+'天</span></div>'+
        '<div class="route-stat"><span class="rlabel">班次</span><span class="rval">'+r.freq+'</span></div>'+
        '<div class="route-stat"><span class="rlabel">吞吐量</span><span class="rval">'+r.volume+'</span></div>'+
        '<div class="route-stat"><span class="rlabel">适合货类</span><span class="rval">'+r.type+'</span></div>'+
      '</div>'+
    '</div>';
  }).join('');

  // ECharts treemap
  setTimeout(function(){
    if(typeof echarts==='undefined'){console.warn('ECharts not loaded');return}
    var ch=echarts.init($('route-chart'));
    ch.setOption({
      title:{text:'洋浦港航线 · 航程天数分布',left:'center',top:8,textStyle:{fontSize:15,color:'#0f2640',fontWeight:600}},
      tooltip:{trigger:'item',formatter:function(p){return p.name+'<br/>航程: <b>'+p.value+'天</b>'}},
      series:[{
        type:'treemap',roam:false,width:'92%',height:'78%',top:50,
        data:routes.map(function(r){return {name:r.port.split(' (')[0]+'\\\n('+r.country+')',value:r.days}}),
        label:{show:true,fontSize:11,color:'#fff',formatter:function(p){return p.name.replace('\\n',' ')}},
        itemStyle:{borderColor:'#faf8f5',borderWidth:3,borderRadius:6},
        levels:[{},{colorSaturation:[0.25,0.55]}],
        color:['#1a3a5c','#2a5a8c','#1e8449','#0d9488','#b8860b','#d4756b','#3a6a5c','#5a5a8c','#6b8e9e','#4a7c59','#8b6b4a','#c4a45a']
      }]
    });
    window.addEventListener('resize',function(){ch.resize()});
  },300);
}
renderRoutes();
</script></body></html>"""





KNOWLEDGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>知识库 · 海南跨境贸易</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
""" + SHARED_CSS + """</head><body>
""" + SHARED_NAV.format("","","","","","","active") + """
<div class="hero" style="padding:40px 24px">
  <div class="hero-badge">KNOWLEDGE BASE</div>
  <h2 style="font-size:32px">知识库</h2>
  <p>政策解读 · 风险分析 · 技术架构 · 研究文章</p>
</div>

<div class="section">
  <div class="section-header"><h3>📅 封关政策时间线</h3></div>
  <div id="timeline"></div>
</div>

<div class="section">
  <div class="section-header"><h3>🛡 风险预警与合规</h3></div>
  <div class="insight-bar"><div class="insight-label">💡 风控洞察</div>海口海关已建立29.7亿条大数据池+147个风险特征库+93个AI模型，实现7×24智能风控。海南的外贸信用管理体系覆盖7万+家企业，是其他自贸区尚未具备的差异化优势。</div>
  <div class="charts-row2"><div class="chart-card" id="rk1"></div><div class="chart-card" id="rk2" style="height:360px"></div></div>
  <div class="card-grid" id="risk-cards"></div>
</div>

<div class="section">
  <div class="section-header"><h3>⚙ 技术架构</h3></div>
  <div class="charts-row2"><div class="chart-card" id="ar1"></div><div class="chart-card" id="ar2" style="height:380px"></div></div>
  <div id="arch-list"></div>
</div>

<div class="section">
  <div class="section-header"><h3>🎯 AI应用场景详解</h3></div>
  <div class="card-grid" id="scenarios-cards"></div>
</div>

<div class="section">
  <div class="section-header"><h3>📝 研究文章与分析报告</h3></div>
  <div class="filter-bar" style="margin:20px 24px;padding:18px;background:rgba(26,58,92,0.04);border-radius:12px">
  <input id="kb-search" class="filter-search" placeholder="🔍 搜索文章标题、内容、关键词..." style="padding:10px 16px;width:100%;max-width:420px;border:1px solid var(--border);border-radius:8px;font-size:14px;margin-bottom:12px" onkeydown="if(event.key==='Enter')filterKB()">
  <div class="chip-row" id="kb-chips" style="display:flex;gap:8px;flex-wrap:wrap">
    <button class="chip active" onclick="filterKBType('all', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--navy);background:var(--navy);color:#fff;cursor:pointer;font-size:13px">全部</button>
    <button class="chip" onclick="filterKBType('贸易政策', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer;font-size:13px">📜 贸易政策</button>
    <button class="chip" onclick="filterKBType('AI赋能', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer;font-size:13px">🤖 AI赋能</button>
    <button class="chip" onclick="filterKBType('实操指南', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer;font-size:13px">📋 实操指南</button>
    <button class="chip" onclick="filterKBKw('关税', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer;font-size:13px">🏷️ 关税</button>
    <button class="chip" onclick="filterKBKw('自贸港', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer;font-size:13px">🏷️ 自贸港</button>
    <button class="chip" onclick="filterKBKw('洋浦港', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer;font-size:13px">🚢 洋浦港</button>
    <button class="chip" onclick="filterKBKw('RCEP', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer;font-size:13px">🌏 RCEP</button>
    <button class="chip" onclick="filterKBKw('封关', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer;font-size:13px">🚪 封关</button>
    <button class="chip" onclick="filterKBKw('原产地', this)" style="padding:6px 14px;border-radius:14px;border:1px solid var(--border);background:#fff;color:var(--text);cursor:pointer;font-size:13px">🏷️ 原产地</button>
  </div>
</div>
<div class="card-grid" id="articles-grid"></div>
</div>

<div class="footer"><p>海南AI跨境贸易 · 企业出海知识库 v5.2</p></div>
""" + AI_WIDGET + """
<script>
const A='/api';const $=id=>document.getElementById(id);
async function F(u){const r=await fetch(u);return r.json()}
async function showArticle(id){const a=await F(A+'/article/'+id);document.getElementById('mob').innerHTML='<h2 style="font-size:20px;color:var(--navy);margin-bottom:12px">'+a.title+'</h2><div style="font-size:13px;color:var(--subtle);margin-bottom:16px">'+a.article_type+' / '+a.created_at+'</div><div style="font-size:15px;color:var(--text);line-height:1.9">'+a.content+'</div>';document.getElementById('mod').classList.add('s')}
async function i(){
  constconst [timeline,risks,archData,scenarios,articles]=await Promise.all([F(A+'/timeline'),F(A+'/risks'),F(A+'/tech_arch'),F(A+'/scenarios'),F(A+'/articles')]);window.risks=risks;window.archData=archData;

  // Timeline
  document.getElementById('timeline').innerHTML='<div style="position:relative;padding-left:24px"><div style="position:absolute;left:8px;top:0;bottom:0;width:2px;background:var(--border)"></div>'+timeline.map(t=>'<div style="position:relative;margin-bottom:18px;padding-left:22px"><div style="position:absolute;left:-20px;top:6px;width:10px;height:10px;border-radius:50%;background:var(--navy);border:2px solid var(--border)"></div><div style="font-size:13px;color:var(--coral);margin-bottom:2px">'+t.event_date+'</div><div style="font-size:15px;color:var(--navy);font-weight:600">'+t.event_title+'<span style="display:inline-block;font-size:11px;padding:2px 10px;border-radius:8px;margin-left:8px;background:rgba(26,58,92,0.06);color:var(--navy)">'+t.category+'</span></div><div style="font-size:14px;color:var(--subtle);margin-top:4px">'+t.event_desc+'</div></div>').join('')+'</div>';

  // Risk cards
  document.getElementById('risk-cards').innerHTML=risks.map(r=>'<div class="info-card"><h4>'+r.risk_type+'<span style="margin-left:8px;font-size:12px;color:'+(r.risk_level.includes('高')?'var(--coral)':'var(--gold)')+'">'+r.risk_level+'</span></h4><p>'+r.description+'</p><p style="margin-top:8px;color:var(--navy);font-size:13px">💡 '+r.solution+'</p><p style="margin-top:4px;color:var(--green);font-size:12px">🏝️ 海南：'+r.hainan_measure+'</p></div>').join('');

  // Architecture
  document.getElementById('arch-list').innerHTML=archData.map(a=>'<div style="display:flex;gap:14px;align-items:flex-start;padding:14px 0;border-bottom:1px solid var(--border)"><div style="width:40px;height:40px;background:var(--navy);color:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">'+a.layer_order+'</div><div><h4 style="font-size:15px;color:var(--navy)">'+a.layer_name+'</h4><p style="font-size:13px;color:var(--subtle)">'+a.description+'</p><div style="font-size:12px;color:var(--navy);margin-top:4px">'+a.components+'</div></div></div>').join('');

  // Scenarios cards
  document.getElementById('scenarios-cards').innerHTML=scenarios.map(s=>'<div class="info-card"><div style="font-size:28px;margin-bottom:8px">'+s.icon+'</div><h4>'+s.name+'</h4><p>"'+s.slogan+'"</p><p style="margin-top:6px;font-size:13px;color:var(--subtle)">'+s.key_data+'</p><p style="margin-top:4px;font-size:12px;color:var(--coral)">📍 '+s.local_case.substring(0,35)+'…</p></div>').join('');

  // Articles
  _allArticles=articles;document.getElementById('articles-grid').innerHTML=articles.map(a=>{const c='background:rgba(26,58,92,0.06);color:var(--navy)';return '<div class="info-card" onclick="showArticle('+a.id+')" style="cursor:pointer"><span style="display:inline-block;padding:3px 10px;border-radius:8px;font-size:11px;font-weight:600;margin-bottom:10px;'+c+'">'+a.article_type+'</span><h4>'+a.title+'</h4><p>'+a.summary+'</p><div style="font-size:12px;color:var(--subtle);margin-top:8px">📅 '+a.created_at+'</div></div>'}).join('');

let _allArticles = [];
function filterKB() {
  const q = (document.getElementById('kb-search').value || '').toLowerCase();
  renderKB(_allArticles.filter(a => (a.title + a.summary + a.content).toLowerCase().includes(q)));
}
function filterKBType(type, btn) {
  document.querySelectorAll('#kb-chips .chip').forEach(c => c.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const list = type === 'all' ? _allArticles : _allArticles.filter(a => a.article_type === type);
  renderKB(list);
}
function filterKBKw(kw, btn) {
  document.querySelectorAll('#kb-chips .chip').forEach(c => c.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderKB(_allArticles.filter(a => (a.title + a.summary + a.content).includes(kw)));
}
function renderKB(list) {
  document.getElementById('articles-grid').innerHTML = list.map(a => 
    '<div class="info-card" onclick="showArticle(' + a.id + ')" style="cursor:pointer">' +
    '<h4>' + a.title + '</h4>' +
    '<p style="font-size:13px;color:var(--subtle);margin-top:6px">' + (a.summary || '').substring(0, 100) + '</p>' +
    '<div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap">' +
    '<span class="tag type">' + (a.article_type || '通用') + '</span>' +
    '<span style="font-size:11px;color:var(--subtle)">' + (a.created_at || '') + '</span>' +
    '</div></div>'
  ).join('') || '<p style="color:var(--subtle);text-align:center;padding:40px">未匹配到文章。试试其他关键词？</p>';
}

  // Charts after DOM load
    setTimeout(async()=>{
  // Fetch data independently for charts
  const [risks,archData]=await Promise.all([fetch('/api/risks').then(r=>r.json()),fetch('/api/tech_arch').then(r=>r.json())]);
  if(typeof echarts==='undefined')return;
  // Risk bar chart
  const rk1=echarts.init(document.getElementById('rk1'));rk1.setOption({tooltip:{trigger:'axis'},legend:{data:['\u98ce\u9669','\u5df2\u8986\u76d6'],top:5},xAxis:{type:'category',data:risks.map(r=>r.risk_type)},yAxis:{type:'value'},series:[{type:'bar',data:risks.map(r=>({value:1,itemStyle:{color:r.risk_level.includes('\u9ad8')?'#d4756b':'#b8860b'}})),barWidth:22},{type:'bar',data:risks.map(()=>({value:1,itemStyle:{color:'#1a3a5c'}})),barWidth:22,label:{show:true,position:'top',formatter:'\u2713',fontSize:16}}]});
  // Radar chart
  const rk2=echarts.init(document.getElementById('rk2'));rk2.setOption({radar:{indicator:[{name:'\u8986\u76d6',max:100},{name:'\u901f\u5ea6',max:100},{name:'\u65b9\u6848',max:100},{name:'\u914d\u5957',max:100},{name:'\u53ef\u7528',max:100}]},series:[{type:'radar',data:[{value:[85,80,82,88,75],name:'\u98ce\u63a7\u4f53\u7cfb',areaStyle:{color:'rgba(26,58,92,0.08)'}}],lineStyle:{color:'#1a3a5c',width:2}}]});
  // Tech arch treemap
  const ar1=echarts.init(document.getElementById('ar1'));ar1.setOption({tooltip:{},series:[{type:'treemap',data:archData.map(t=>({name:t.layer_name,value:(6-t.layer_order)*20,children:(t.components||'').split(' / ').map(c=>({name:c.trim(),value:8+(Math.random()*8|0)}))})),label:{color:'#fff',fontSize:10},levels:[{},{itemStyle:{borderColor:'#faf8f5',borderWidth:2}},{colorSaturation:[0.3,0.6]}]}]});
  // Tech radar
  const ar2=echarts.init(document.getElementById('ar2'));ar2.setOption({radar:{indicator:[{name:'\u6a21\u5757',max:100},{name:'\u6269\u5c55',max:100},{name:'\u5b89\u5168',max:100},{name:'\u5b9e\u65f6',max:100},{name:'\u517c\u5bb9',max:100}]},legend:{data:archData.map(a=>a.layer_name),bottom:0},series:[{type:'radar',data:archData.map((t,i)=>({value:[95-i*5,90-i*8,85+i*3,80+i*5,85],name:t.layer_name})),lineStyle:{width:2}}],color:['#1a3a5c','#1e8449','#b8860b','#d4756b','#6b8e9e']});
},2000)
}
i();window.addEventListener('DOMContentLoaded',function(){setTimeout(async()=>{const[risks,aD]=await Promise.all([fetch('/api/risks').then(r=>r.json()),fetch('/api/tech_arch').then(r=>r.json())]);if(typeof echarts==='undefined')return;echarts.init(document.getElementById('rk1')).setOption({tooltip:{trigger:'axis'},legend:{data:['风险','已覆盖'],top:5},xAxis:{type:'category',data:risks.map(r=>r.risk_type)},yAxis:{type:'value'},series:[{type:'bar',data:risks.map(r=>({value:1,itemStyle:{color:r.risk_level.includes('高')?'#d4756b':'#b8860b'}})),barWidth:22},{type:'bar',data:risks.map(()=>({value:1,itemStyle:{color:'#1a3a5c'}})),barWidth:22,label:{show:true,position:'top',formatter:'✓',fontSize:16}}]});echarts.init(document.getElementById('rk2')).setOption({radar:{indicator:[{name:'覆盖',max:100},{name:'速度',max:100},{name:'方案',max:100},{name:'配套',max:100},{name:'可用',max:100}]},series:[{type:'radar',data:[{value:[85,80,82,88,75],name:'风控',areaStyle:{color:'rgba(26,58,92,0.08)'}}],lineStyle:{color:'#1a3a5c',width:2}}]});echarts.init(document.getElementById('ar1')).setOption({tooltip:{},series:[{type:'treemap',data:aD.map(t=>({name:t.layer_name,value:(6-t.layer_order)*20,children:(t.components||'').split(' / ').map(c=>({name:c.trim(),value:8+(0|Math.random()*8)}))})),label:{color:'#fff',fontSize:10},levels:[{},{itemStyle:{borderColor:'#faf8f5',borderWidth:2}},{colorSaturation:[0.3,0.6]}]}]});echarts.init(document.getElementById('ar2')).setOption({radar:{indicator:[{name:'模块',max:100},{name:'扩展',max:100},{name:'安全',max:100},{name:'实时',max:100},{name:'兼容',max:100}]},legend:{data:aD.map(a=>a.layer_name),bottom:0},series:[{type:'radar',data:aD.map((t,i)=>({value:[95-i*5,90-i*8,85+i*3,80+i*5,85],name:t.layer_name})),lineStyle:{width:2}}],color:['#1a3a5c','#1e8449','#b8860b','#d4756b','#6b8e9e']})},3000);});
</script>
<div class="mo" id="mod"><div class="mc"><button class="cl" onclick="document.getElementById('mod').classList.remove('s')">✕</button><div id="mob"></div></div></div>
<script>
// Standalone KB render + filter
(function(){
  const $ = id => document.getElementById(id);
  let allArticles = [];
  function render(list){
    const grid = $('articles-grid');
    if (!grid) return;
    if (!list || !list.length) {
      grid.innerHTML = '<p style="color:var(--subtle);text-align:center;padding:40px">未匹配到文章。试试其他关键词？</p>';
      return;
    }
    grid.innerHTML = list.map(a => 
      '<div class="info-card" onclick="showArticle(' + a.id + ')" style="cursor:pointer">' +
      '<span style="display:inline-block;padding:3px 10px;border-radius:8px;font-size:11px;font-weight:600;margin-bottom:10px;background:rgba(26,58,92,0.06);color:var(--navy)">' + (a.article_type || '通用') + '</span>' +
      '<h4 style="margin:6px 0">' + a.title + '</h4>' +
      '<p style="font-size:13px;color:var(--subtle)">' + (a.summary || '').substring(0, 120) + '</p>' +
      '<div style="font-size:12px;color:var(--subtle);margin-top:8px">📅 ' + (a.created_at || '') + '</div>' +
      '</div>'
    ).join('');
  }
  window._renderKB = render;
  
  async function init() {
    try {
      const r = await fetch('/api/articles');
      allArticles = await r.json();
      render(allArticles);
      document.body.addEventListener('click', function(e) {
        const chip = e.target.closest && e.target.closest('#kb-chips .chip');
        if (!chip) return;
        document.querySelectorAll('#kb-chips .chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        const onclick = chip.getAttribute('onclick') || '';
        const m = onclick.match(/filterKB(Type|Kw)\(['"](.+?)['"]/);
        if (!m) return;
        const mode = m[1], val = m[2];
        if (mode === 'Type') {
          render(val === 'all' ? allArticles : allArticles.filter(a => a.article_type === val));
        } else {
          render(allArticles.filter(a => (a.title + a.summary + a.content).includes(val)));
        }
      });
      const search = $('kb-search');
      if (search) {
        search.addEventListener('keydown', function(e){
          if (e.key === 'Enter') {
            const q = (search.value || '').toLowerCase();
            render(allArticles.filter(a => (a.title + a.summary + a.content).toLowerCase().includes(q)));
          }
        });
      }
    } catch(e) { console.error('KB init error:', e); }
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>
</body></html>"""
# ==================== MAIN ====================
if __name__ == "__main__":
    print("init DB v5.2...")
    init_db()
    port = int(os.environ.get("PORT", 8080))
    print(f"http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

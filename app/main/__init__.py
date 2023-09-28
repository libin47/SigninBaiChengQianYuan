# -*- coding: utf-8 -*-
"""
@Author:waiwen
@Time: 2020/5/13 14:27
@Email: iwaiwen@163.com
@Software: PyCharm
@File    : __init__.py.py
"""
import json
import qrcode
from io import BytesIO
import pickle
from database_mongo import getdb_user, getdb_dingcan
import requests

from flask import render_template, jsonify, make_response
from flask import Blueprint, request, redirect, url_for, flash, send_file
from flask_login import login_user, login_required, logout_user
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Length, DataRequired, Optional
from flask_wtf.form import FlaskForm
from flask_login import LoginManager

# from GaoKao2022.SQL.setting import AuthINFO

from app.auth.auth import Auth
import tracemalloc
import time

b = Blueprint("main", __name__)

k_title = "工业互联网一体化进园区进企业“百城千园行”活动暨企业数字化转型发展推进行动"
k_title_city = "（康保站）"
k_title_sub = "百城千园行-康保站"
k_local = "河北省张家口市康保县中共康保县委党校前楼会议厅"
k_elocal = ""
k_zuowei = "../static/座位表.png"
k_time = [
    {"type": "main", "text": "9月27日-上午"},
    {"time":"08:00-09:00", "text":"报到（河北省张家口市康保县中共康保县委党校前楼会议厅）"},
    {"time":"09:00-09:05", "text":"主持人介绍与会领导和嘉宾"},
    {"time":"09:05-09:10", "text":"领导致辞：康保县政府分管领导致辞"},
    {"time":"09:10-09:15", "text":"领导致辞：中国联合网络通信有限公司张家口市分公司副总经理致辞"},
    {"time":"09:15-09:35", "text":"领导致辞：市工业和信息化局分管领导致辞"},
    {"time":"09:35-09:55", "text":"主题演讲：工业互联网赋能新型能源"},
    {"time":"09:55-10:10", "text":"主题演讲：降本增效，精益生产，锐捷网络企业数字园区解决方案介绍"},
    {"time":"10:10-10:25", "text":"主题演讲：AI赋能智慧风电场的可视化辅助"},
    {"time":"10:25-10:40", "text":"签约仪式"},
    {"time":"10:40-10:50", "text":"茶歇及观展"},
    {"time":"10:50-11:00", "text":"案例分享：河北凯阔食品集团股份有限公司就信息化建设进行分享"},
    {"time":"11:00-11:05", "text":"中国银行张家口分行做“数字贷”产品推介"},
    {"time":"11:05-11:10", "text":"中国建设银行张家口分行做“数字贷”产品推介"},
    {"time":"11:10-11:20", "text":"中国银行张家口分行做数字人民币应用推介"},
    {"time":"11:20-12:00", "text":"自由对接"},
    {"time":"12:00", "text":"就餐"},
    {"type": "main", "text": "9月27日-下午"},
    {"time":"14:00", "text":"精准对接——工业企业与专家、服务商、金融机构及有关院校进行精准对接，深入企业现场洽谈"},
]
k_xuzhi = [
    {"type": "title", "text": "会议须知"},
    {"type": "text", "text": "您好!欢迎您来参加工业互联网一体化进园区进企业“百城千园行”活动暨企业数字化转型发展推进行动(康保站)，为确保会议的顺利进行，请您关注以下事项。"},
    {"type": "left", "text": "一、严格遵守会议纪律"},
    {"type": "text", "text": "1、会议开始后，请将手机关闭或置于静音状态，保持会场安静，不得在会场内接打电话，不得随意走动。"},
    {"type": "text", "text": "2、会场内请勿吸烟，保持会场清洁。"},
    {"type": "text", "text": "3、会场内摄像、录音统一由会务组安排。"},
    {"type": "text", "text": "4、与会人员会议期间如需帮助请与会务组联系，会务人员联系方式如下："},
    {"type": "text", "text": "会务经理:薛大伟 18603235802"},
    {"type": "text", "text": "酒店经理:郝志龙（餐饮） 13373337703"},
    {"type": "text", "text": "酒店经理:赵博超（会议） 15930351711"},
    {"type": "left", "text": "二、会议时间和地点"},
    {"type": "text", "text": "1、会议时间:"},
    {"type": "text", "text": "2023年9月27日（星期三）"},
    {"type": "text", "text": "2、会议地点:"},
    {"type": "text", "text": "河北省张家口市康保县中共康保县委党校前楼会议厅"},
    {"type": "text", "text": "3、就餐地点:"},
    {"type": "text", "text": "河北省张家口市康保县中共康保县委党校后楼自助餐厅"},
]
k_jianjie = [
    {"type": "title", "text": "康保县简介"},
    {"type": "text", "text": "康保县位于河北省最西北部，县境东、北、西三面与内蒙古自治区接壤，平均海拔1450米，气候高寒干旱，年均气温2.1C，无霜期100天左右，年均降水量330毫米。县城总面积3365平方公里，辖7镇8乡326个行政村、585个自然村，1个省级经济开发区、1个怡安康城管委会，总人口26.2万， 常住人口13.8万。 曾是国家扶贫开发工作重点县，也是河北省十个深度贫困县之一，2020年底，8.8万农村贫困人口全部脱贫，195个贫困村全部出列，全县脱贫摘帽，被省委、省政府授予“全省脱贫攻坚先进集体”。"},
    {"type": "text", "text": "2023年上半年，全县地区生产总值完成27.65亿元，同比增长2.2%，增速在全市排第15位;规上工业增加值实现8.28亿元，同比增长8.1%，增速在全市排第9位;固定资产投资完成14.71 亿元，同比增长4.1%，增速在全市排第14位;社会消费品零售总额完成4.28亿元，同比增长2.2%，增速在全市排第14位;全部财政收入完成4.67亿元，同比增长46.8%，增速在全市排第3位;城乡居民人均可支配收入分别完成19618元、8616元，同比增长分别为6.4%、7.9%，增速在全市排名分别为第3位、第9位。"},
    {"type": "text", "text": " 历史发展沿革。康保县是张库大道的必经之路，有着重要的战略地位，曾是军草、畜产品的主要供给地之一。1925年康保正式建县，属察哈尔省管辖，1945年康保县人民政府民冀察区十九专区，1952年改属河北省张家口专区。新中国成立后，在党的领导下， 康保人民积极投身到社会主义革命和建设的伟大事业。改革开放30多年来，特别是脱贫攻坚战役期间，历届县委、政府团结带领全县人民攻坚克难、踏厉奋发，与自身相比康保县发生了巨大的变化， 经济实力显著增强，城乡面貌日新月异，生活水平明显提高。"},
    {"type": "text", "text": "生态环境良好。康保天蓝、地绿、水净、气爽，是旅游度假、避暑纳凉、休闲养老的理想之地。空气洁净清新，国家二级标准以上天数常年保持在320天以上，1-8月PM2.5平均浓度9微克/立方米，大气质量持续全省领先;地下水PH值为7.4-7.8，富含钾、钙、钠、镁等多种矿物质元素，是天然的饮用矿泉水;土地资源丰富，拥有耕地211万亩、林地118万亩、草场150万亩，林木绿化率31.3%，草场盖度65%;境内无排污企业，土地无污染，农产品具备绿色有机、无公害、养分高等特点，康保苦菜、胡麻油等6个品牌被认定为国家地理标志商标，“康保柴胡” 入选中药材“十大冀药”产业大县名单。"},
    {"type": "text", "text": "风光资源充裕。康保境内主风向稳定，风功率密度达到国标4-7级，平均风速6.6米/秒，可建设550万千瓦大型风电场。年日照时数达3100小时，是全省光照时间最长的县，为二类地区，仅次于青藏高原，具备200万千瓦光伏发电能力。目前，全县风光电获批716万千瓦，并网总规模达到557万千瓦，年制氢8000吨的鸿蒙新能源风光电制氢一期项目已经开工建设，新能源成为名副其实的支柱产业。"},
    {"type": "text", "text": "文化底蕴深厚。康保在历史上属辽金满蒙民族游牧之地，在这里形成了“马背文化”与“农耕文化”相互交融的民俗风情和独具特色的地方文化，孕育 了康保人民秀内慧中、勤劳淳朴、诚信直爽的个性。境内国家级文物保护单位“金长城”遗址东西横贯全境，新石器时代兴隆历史文化遗存群保存相对完整:“康保二人台”被国务院列入首批国家非物质文化遗产保护名录，我县被誉为“中国民间文化艺术之乡”“二人台艺术之乡”， 康巴诺尔湖列入国家级湿地公园名录，是国家级保护动物遗鸥的主要繁殖地，被中国野生动物保护协会命名为“中国遗鸭之乡”"},
    {"type": "text", "text": " 产业蓬勃发展。坚持把项目建设作为经济发展的切入点和突破口，紧紧围绕做大做强清洁能源、特色农牧、京张体育文化旅游三大主导产业，制定出台了扶持重点产业发展、招商引资奖励、返乡入乡创业扶持等政策措施，打出政策“组合拳”，持续拉长产业链条，扩大有效投资。可再生能源方面，抢抓张家口建设国家级可再生能源示范区机遇，加快推进鸿蒙新能源和制氢项目建设进度，引进氢能产业园、风储一体化等新能源综合产业项目落户康保，推动绿电在制氢、存储等领域广泛应用，着力构建风、光、储、氢、生物质能“五位一体”新能源体系，实现新能源产业集群发展、绿色发展。特色农牧方面，在做大做强皇世等农业龙头企业的基础上，引进内蒙古为生科技等一批生产型农牧龙头企业落户康保，全力打造生态、高效、质优的现代化高端有机农业。体育文化旅游方面，按照“专业化、赛事化旅游，生态型、旅居型康养”发展思路，坚持专业团队干专业事，深挖资源禀赋和人文历史，谋划实施以生态、马术、足球、太极、军旅为主题的特色文旅项目，新建全民冰雪体育综合体、公共体育场、二人台文化传播中心等，成功举办了遗鸥保护摄影周、草原马拉松、二人台艺术周、NCC全国机车越野争霸赛、全民丰收节等系列活动，全力融入京张体育文化旅游带建设。"},
    {"type": "title", "text": "尚义县基本情况"},
    {"type": "text", "text": "尚义县地处河北省西北部，晋冀蒙三省交界处，总面积2601平方公里，其中林地面积170万亩，森林覆盖率38.9%；草地面积127万亩，林草盖度达76.2%。全县分坝上、坝下两个地貌单元，坝上是草原地貌，坝下属丘陵浅山区，平均海拨1300米，年降水量330—420毫米，年平均气温3.6℃，无霜期100天—120天。全县辖7镇7乡1个安置区管委会，172个行政村，总人口18.24万人，常住人口10.42万人，城镇化率54.19%。"},
    {"type": "text", "text": "尚义历史文化厚重。尚义于1936年建县，由时任察哈尔省主席宋哲元起名，寓“崇尚礼义”之意，军台文化、柔玄古镇、明长城等在此交汇融合，四台遗址入选“2022年中国六大考古新发现”。尚义资源禀赋独特。年均日照时数2776.8小时，年均有效风速时数在7200小时以上，年平均风速达3.2m/s以上，风能、太阳能均属国家二类优质资源区，风光电并网总量达437.2万千瓦，约占全市1/6。尚义农业基础较好。全县光照充足，气候冷凉，非常适宜发展特色种养产业，白萝卜、生菜等绿色无公害蔬菜远销日本、韩国等国家和地区。燕麦、草莓、西瓜、肉鸡等特色农业产业效益显著，成为带动贫困户增收的支柱产业。尚义燕麦获得“河北省特色农产品优势区”称号。尚义生态环境良好。境内河流淖泊众多，拥有大青山国家森林公园、察汗淖尔国家湿地公园、石人背地质公园等自然旅游景区，草原天路西线贯通东西，“赛羊”“冰雪”旅游品牌效应日渐突显，是避暑旅游、休闲度假的理想之地，十三号村荣获“2020年中国美丽休闲乡村”称号。"},
    {"type": "text", "text": "近年来，全县坚持以习近平新时代中国特色社会主义思想为指引，积极抢抓首都“两区”、京张体育文化旅游带、河北“两翼”等战略机遇，大力实施“产业提质增效、乡村全面振兴、城市扩能提质、改革创新赋能、民生普惠共享、生态治理提级、社会治理创优”七大工程，经济社会和各项事业取得了新成效、开辟了新局面。2023年1-7月份，全县地区生产总值增长4.4%；规上工业增加值增长10.9%；固定资产投资增长1.2%；社会消费品零售总额增长3.3%；城镇和农村居民人均可支配收入分别增长6%和8%。"},
]
k_chengche = [
    {"type": "title", "text": "乘车安排"},
    {"type": "left", "text": "一、时间"},
    {"type": "text", "text": "9月27日下午14:00"},
    {"type": "left", "text": "二、内容"},
    {"type": "text", "text": "嘉宾由河北省张家口市康保县中共康保县委党校前楼会议厅前门集体乘车赴河北凯阔食品集团股份有限公司、张家口皇世食品有限公司"},
    {"type": "left", "text": "三、乘客"},
    {"type": "text", "text": "联通雄安产业互联网有限公司专家 "},
    {"type": "text", "text": "浙江大华技术股份有限公司专家 "},
    {"type": "text", "text": "锐捷网络股份有限公司专家"},
    {"type": "text", "text": "有关金融机构及院校"},
    {"type": "text", "text": "张家口市工信局主要负责人"},
    {"type": "text", "text": "康保县发展和改革局主要负责人"},
    {"type": "text", "text": "康保县联通主要负责人"},
    {"type": "left", "text": "四、引导车"},
    {"type": "text", "text": "冀GE1990 "},
    {"type": "left", "text": "五、联络员"},
    {"type": "text", "text": "闫雅楠 18531318133"},
]

@b.route("/MP_verify_TTH4vMTo8zLwTLXd.txt", methods=["GET"])
def wxyanzheng():
    return render_template("MP_verify_TTH4vMTo8zLwTLXd.txt")

@b.route("/", methods=["GET"])
@b.route("/index", methods=["GET"])
def index():
    kwarg = {"title": k_title, "city": k_title_city}
    return render_template("index.html", **kwarg)

@b.route("/timeanpai", methods=["GET"])
def timeanpai():
    kwarg = {"title": k_title_sub, "time": k_time}
    return render_template("timeanpai.html", **kwarg)

@b.route("/weather", methods=["GET"])
def weather():
    kwarg = {"title": k_title_sub}
    return render_template("weather.html", **kwarg)
    
@b.route("/huiyixuzhi", methods=["GET"])
def huiyixuzhi():
    kwarg = {"title": k_title_sub, "xuzhi": k_xuzhi}
    return render_template("huiyixuzhi.html", **kwarg)

@b.route("/zuowei", methods=["GET"])
def zuowei():
    kwarg = {"title": k_title_sub, "img": k_zuowei}
    return render_template("zuowei.html", **kwarg)

@b.route("/chengche", methods=["GET"])
def chengche():
    kwarg = {"title": k_title_sub, "chengche":k_chengche}
    return render_template("chengche.html", **kwarg)

@b.route("/city", methods=["GET"])
def wanquan():
    kwarg = {"title": k_title_sub, "jianjie": k_jianjie}
    return render_template("city.html", **kwarg)


@b.route("/zuoweiimage", methods=["GET"])
def zuoweiimage():
    import base64
    img_stream = ''
    with open("app/static/座位表.png", 'r') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream)
    return img_stream









@b.route("/index/<openid>", methods=["GET"])
def index_openid(openid):
    db = getdb_user()
    data = db.find_one({"openid": openid})
    db.close()

    name = data['name']
    phone = data['phone']
    kwargs = {
        "name": name,
        "phone": phone,
        "openid": openid
    }
    return render_template('index.html', **kwargs)
    # response = make_response(render_template('index.html', **kwargs))
    # response.headers['Cache-Control'] = 'no-store'
    # return response



@b.route("/dingcanpinzheng", methods=["GET"])
def dingcanpinzheng():
    time = request.args.get("time")
    openid = request.args.get("openid")
    value = request.args.get("value")
    db = getdb_user()
    data = db.find_one({"openid": openid})
    db.close()
    name = data['name']
    phone = data['phone']

    db = getdb_dingcan()
    number = db.count_documents({"openid": openid, "date": int(time), "value": int(value)})
    db.close()

    kwargs = {
        "name": name,
        "phone": phone,
        "openid": openid,
        "time": "2023年5月%s日"%time,
        "value": ["早饭", "午饭", "晚饭"][int(value)],
    }
    if number > 0:
        kwargs["ok"] = 1
        kwargs['png'] = "/dingcanpinzhengpng?openid="+openid+"&time="+time+"&value="+value
        return render_template("dingcanpinzheng.html", **kwargs)
    else:
        kwargs["ok"] = 0
        return render_template("dingcanpinzheng.html", **kwargs)


@b.route("/dingcanpinzhengpng", methods=["GET"])
def dingcanpinzhengpng():
    time = request.args.get("time")
    openid = request.args.get("openid")
    value = request.args.get("value")
    db = getdb_dingcan()
    number = db.count_documents({"openid": openid, "date": int(time), "value": int(value)})
    db.close()
    if number > 0:
        codeimg = qrcode.make("https://wxapp.wind-watcher.cn/dingcanpinzheng?openid="+openid+"&time="+time+"&value="+value)
        img_io = BytesIO()
        codeimg.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    return render_template("dingcan.html")
    
@b.route("/dingcan/<openid>", methods=["GET"])
def dingcan(openid):
    db = getdb_dingcan()
    data = [
        db.count_documents({"openid": openid, "date": 29, "value": 1}),
        db.count_documents({"openid": openid, "date": 29, "value": 2}),
        db.count_documents({"openid": openid, "date": 30, "value": 0}),
        db.count_documents({"openid": openid, "date": 30, "value": 1}),
        db.count_documents({"openid": openid, "date": 30, "value": 2}),
    ]
    db.close()

    kwargs = {
        "openid": openid,
        "data": data
    }
    return render_template("dingcan.html", **kwargs)



@b.route("/signin_ok", methods=["GET"])
def signin_ok():
    return render_template("signin.html")

@b.route("/login2/<openid>", methods=["GET"])
def signin2(openid):
    kwargs = {
        "openid": openid
    }
    return render_template("login.html", **kwargs)


@b.route("/login", methods=["GET"])
def signin():
    code = request.args.get("code")
    # return redirect("/index/" + code)
    APPID = "wxcd05e9f3d5d1f7bf"
    SECRET = "07f346d84f65d5ac9c5875e04599d6b0"
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=' + APPID + '&secret=' + SECRET + '&code=' + code + '&grant_type=authorization_code'
    r = requests.get(url)
    data = r.json()
    if 'errcode' in data.keys():
        return redirect("/index")
    else:
        openid = data['openid']
        db = getdb_user()
        num = db.count_documents({"openid": openid})
        if num > 0:
            return redirect("/index/"+openid)
        else:
            kwargs = {
                "openid": openid
            }
            return render_template("login.html", **kwargs)


@b.route("/signup", methods=["POST"])
def signup():
    d = json.loads(request.get_data(as_text=True))
    name = str(d["name"])
    phone = int(d.get("phone"))
    danwei = str(d["danwei"])
    openid = str(d['openid'])
    # times = time.localtime()
    db = getdb_user()
    db.insert_one({
        "name": name,
        "phone": phone,
        "danwei": danwei,
        "openid": openid,
    })
    return jsonify({"ok": True})

@b.route("/dingcan_api", methods=["POST"])
def dingcan_api():
    d = json.loads(request.get_data(as_text=True))
    openid = str(d["openid"])
    date = int(d["time"])
    value = int(d["value"])
    # 验证
    mon = time.localtime( time.time() ).tm_mon
    day = time.localtime( time.time() ).tm_mday
    hour = time.localtime( time.time() ).tm_hour
    hour_limit = [9, 14, 19]
    if mon>5:
        return jsonify({"ok": False})
    else:
        if day>date:
            return jsonify({"ok": False})
        elif day==(date):
            if hour > hour_limit[value]:
                return jsonify({"ok": False})

    db = getdb_dingcan()
    db.insert_one({
        "openid": openid,
        "date": date,
        "value": value
    })
    db.close()
    return jsonify({"ok": True})

@b.route("/get_openid", methods=["POST"])
def get_openid():
    d = json.loads(request.get_data(as_text=True))
    code = str(d["code"])
    APPID = "wxcd05e9f3d5d1f7bf"
    SECRET = "07f346d84f65d5ac9c5875e04599d6b0"
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid='+APPID+'&secret='+SECRET+'&code='+code+'&grant_type=authorization_code'
    r = requests.get(url)
    data = r.json()
    if 'errcode' in data.keys():
        return jsonify({"ok": False})
    else:
        openid = data['openid']
        db = getdb_user()
        num = db.count_documents({"openid": openid})
        if num>0:
            return jsonify({"ok": True, "exist": True, 'openid': data['openid']})
        else:
            return jsonify({"ok": True, "exist": False, 'openid': data['openid']})


@b.route("/get_fan_api", methods=["POST"])
def get_fan_api():
    d = json.loads(request.get_data(as_text=True))
    date = int(d["date"])
    fan = int(d["fan"])
    db = getdb_dingcan()
    result = db.coll.aggregate([
        {
           '$match':{
               'date': date,
               'value': fan
           }
        },
        {
            '$lookup':{
                'from': 'user',
                'localField': 'openid',
                'foreignField': 'openid',
                'as': 'result'
            }
        }
    ]
    )
    db.close()
    result = list(result)
    data = []
    for r in result:
        x = dict()
        x['openid'] = r['openid']
        x['date'] = r['date']
        x['value'] = r['value']
        x['len'] = len(r['result'])
        x['name'] = r['result'][0]['name']
        x['phone'] = r['result'][0]['phone']
        x['danwei'] = r['result'][0]['danwei']
        data.append(x)
    return jsonify({"ok": True, "data": data})

@b.route("/get_user_api", methods=["POST"])
def get_user_api():
    db = getdb_user()
    result = db.find({})
    db.close()
    result = list(result)
    data = []
    for r in result:
        r['_id'] = str(r['_id'])
        data.append(r)
    return jsonify({"ok": True, "data": data})





@b.route("/admin", methods=["GET"])
def admin():
    return render_template("admin.html")


@b.route("/log", methods=["GET"])
@login_required
def logpage():
    return render_template("log.html")


class LoginForm(FlaskForm):
    username = StringField("账户名：", validators=[DataRequired(), Length(1, 30)])
    password = PasswordField("密码：", validators=[DataRequired(), Length(1, 64)])
    remember_me = BooleanField("记住密码", validators=[Optional()])


login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "main.login"
login_manager.login_message = "请登录！"
login_manager.login_message_category = "info"


#
# @login_manager.user_loader
# def load_user(id):
#     return Auth(id=1, username=AuthINFO.get("username"), password=AuthINFO.get("password"))

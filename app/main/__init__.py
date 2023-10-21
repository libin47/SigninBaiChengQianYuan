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
k_title_city = "（沽源站）"
k_title_sub = "百城千园行-沽源站"
k_local = "沽源县库伦淖尔旅游度假区开元酒店3楼会议室"
k_elocal = ""
k_zuowei = "../static/座位表.png"
k_time = [
    {"type": "main", "text": "10月23日-上午"},
    {"time":"09:30-10:00", "text":"报到（沽源县库伦淖尔旅游度假区开元酒店3楼会议室）"},
    {"time":"10:00-10:05", "text":"主持人介绍与会领导和嘉宾"},
    {"time":"10:05-10:10", "text":"领导致辞：沽源县政府分管领导致辞"},
    {"time":"10:10-10:15", "text":"领导致辞：中国联合网络通信有限公司张家口市分公司副总经理致辞"},
    {"time":"10:15-10:35", "text":"领导致辞：市工业和信息化局分管领导致辞"},
    {"time":"10:35-10:55", "text":"主题演讲：企业数字化转型的路径"},
    {"time":"10:55-11:10", "text":"主题演讲：工控安全建设思路与实践"},
    {"time":"11:10-11:25", "text":"主题演讲：智慧光伏电站可视化生产辅助系统解决方案"},
    {"time":"11:25-11:30", "text":"签约仪式"},
    {"time":"11:30-11:35", "text":"中国工商银行张家口分行做“数字贷”产品推介"},
    {"time":"11:35-11:40", "text":"中国农业银行张家口分行做“数字贷”产品推介"},
    {"time":"11:40-11:50", "text":"中国银行张家口分行做数字人民币应用推介"},
    {"time":"11:50", "text":"就餐"},
    {"type": "main", "text": "10月23日-下午"},
    {"time":"14:00", "text":"精准对接——工业企业与专家、服务商、金融机构及有关院校进行精准对接，深入企业现场洽谈"},
]
k_xuzhi = [
    {"type": "title", "text": "会议须知"},
    {"type": "text", "text": "您好!欢迎您来参加工业互联网一体化进园区进企业“百城千园行”活动暨企业数字化转型发展推进行动(沽源站)，为确保会议的顺利进行，请您关注以下事项。"},
    {"type": "left", "text": "一、严格遵守会议纪律"},
    {"type": "text", "text": "1、会议开始后，请将手机关闭或置于静音状态，保持会场安静，不得在会场内接打电话，不得随意走动。"},
    {"type": "text", "text": "2、会场内请勿吸烟，保持会场清洁。"},
    {"type": "text", "text": "3、会场内摄像、录音统一由会务组安排。"},
    {"type": "text", "text": "4、与会人员会议期间如需帮助请与会务组联系，会务人员联系方式如下："},
    {"type": "text", "text": "会务经理:常昊字 18603233291"},
    {"type": "text", "text": "酒店经理:王超 15011199819"},
    {"type": "left", "text": "二、会议时间和地点"},
    {"type": "text", "text": "1、会议时间:"},
    {"type": "text", "text": "2023年10月23日（星期一）"},
    {"type": "text", "text": "2、会议地点:"},
    {"type": "text", "text": "沽源县库伦淖尔旅游度假区开元酒店3楼会议室"},
    {"type": "text", "text": "3、就餐地点:"},
    {"type": "text", "text": "库伦淖尔旅游度假区开元大帐"},
]
k_jianjie = [
    {"type": "title", "text": "沽源县简介"},
    {"type": "text", "text": "沽源县位于河北省西北部坝上地区，地处内蒙古高原向华北平原的过渡带，东临承德市丰宁县，南与赤城县、崇礼县相连，西与张北县、康保县毗邻，北与内蒙古锡林郭勒盟正蓝旗、多伦县接壤，总面积3654平方千米，辖4镇、10乡、233个行政村，总人口22.45万。沽源气候条件独特，全县平均海拔1536米，年均气温2.1摄氏度，夏季平均气温17.9摄氏度，年均降水量400毫米左右，无霜期110天，年优良空气天数290天以上。沽源生态系统完好，是滦河、黑河、白河的发源地，全县林地面积192.8万亩，草场面积202万亩，水域面积6.1万亩，湿地面积79.5万亩，是京津冀地区重要的水源地和生态功能区。拥有闪电河国家级湿地公园和葫芦河省级湿地公园。沽源历史文化底蕴深厚，曾是辽、金、元历代帝王的避暑游猎胜地，境内有小宏城遗址、九连城城址、梳妆楼元墓、张库古商道、历代长城等多处历史文化古迹。小宏城遗址、九连城城址和梳妆楼元墓为国家重点文物保护单位。沽源资源能源丰富，已探明铀钼、褐煤、沸石、铅锌等矿产资源20余种。拥有340万千瓦的风能资源，360万千瓦的太阳能资源，是仅次于西藏西部的太阳能辐射二类地区。沽源交通区位独特，现有国省干线7条，张石、张承、二秦高速建成通车，太锡铁路通过省发改委立项。随着交通路网体系的不断完善，我县链接张承蒙、融入环京津的区位优势日益显现。"},
    {"type": "text", "text": "2022年，全县生产总值完成71.3亿元，同比增长8%；固定资产投资同比增长10.7%；规模以上工业增加值同比增长15.2%；社会消费品零售总额同比增长8.4%；全部财政收入完成7.5亿元，同比增长9.8%；一般公共预算收入完成4.48亿元，同比增长12.1%；城乡居民人均可支配收入分别完成34178元、14686元，同比增长7.8％和13.4%。"},
    {"type": "title", "text": "塞北管理区简介"},
    {"type": "text", "text": "塞北管理区前身是河北省国营沽源牧场，始建于1955年，先后隶属国家农业部、河北省农垦局。2003年6月，经省政府批准，正式改制为张家口市塞北管理区，为张家口市委、市政府派出机构，同时挂张家口市高效畜牧业示范区牌子。我区地处北纬41°,西与太仆寺旗接壤，北与正蓝旗相毗，东与丰宁县相邻，南与沽源县相连，是典型的农牧交错带和国际公认的黄金奶源带。全区总面积227平方公里，其中耕地16.8万亩，林地6.16万亩，草地8.89万亩。辖4个管理处，户籍人口6486人，常住人口6804人。近年来，随着产业转型升级、绿色发展的步伐不断加快，在发展质量提升方面获得了国家和省级的认可，先后获批国家农业标准化示范区、全国农垦农机标准化示范农场、省级乳业现代农业园区、国家现代农业示范区、第一批畜牧业绿色发展示范县区、省级农业可持续发展试验示范区、全国农村一二三产业融合发展创建名单。2020年黄土湾草原公园被列入首批国家草原自然公园试点建设名单。2022年，该区坚决贯彻省委、省政府，市委、市政府和区党工委决策部署，坚持稳中求进工作总基调，贯彻新发展理念，融入新发展格局，推动高质量发展，扎实做好“六稳”工作，积极落实“六保”任务，全力稳住了经济基本盘，全年完成地区生产总值14.9亿元，增长4%，完成一般公共预算收入1.9亿元，增长16.8%；规上工业增加值增长3.4%；完成固定资产投资5.6亿元，增长22.3%；完成社会消费品零售总额0.64亿元，增长0.4%。"},
    {"type": "text", "text": "近年来，该区以打造首都“两区”建设先行示范区为目标，立足资源禀赋，发挥比较优势, 抢抓太锡铁路机遇，大力发展四大产业，打造特色小城，推动高质量发展。做强做优特色农牧业。大力发展乳业、薯业、草业，在蒙牛乳业、现代牧业等龙头企业的带动下，形成了集奶牛规模养殖、乳品加工营销、饲草料供应、产品包装配套、沼气发电、粪渣还田的全产业链条和马铃薯组培育苗、种薯繁育、商品薯种植、全粉加工薯业经济产业链。建立河北草地生态系统国家野外科学观测研究站和中国农大草业科学教学基地，为草业发展提供了科技人才支撑。大力发展新型能源业。该区有适合发展40万千瓦的风电区域，有240万千瓦光伏发电潜力，具备发展2个百万千瓦的新能源项目的良好条件。引进了智能微电网、“农光互补”等一批优质项目，构建“发-输-配-售-用”一体化区域智能微电网系统，打造发电、储运、应用一体化新能产业基地。挖掘培育文化旅游业。发展生态农业观光游，建设2个万亩草原公园；探索工业企业科普游，建成蒙牛塞北乳业国家3A级工业景区；拓展地方文化特色游。挖掘塞北地域蒙元文化、农垦文化等特色文化，规划建设沽源牧场场史馆、农垦文化博物馆；打造草原特色赛事游。开展“全国航模比赛”等活动；大力宣传塞北风情，完成了“塞北的雪”影视拍摄。积极发展健康养生业。大力发展健康养老产业，打造“慢生活”特色的养老服务体系，发展“候鸟式”和“度假式”养老。发展健康旅游产业,发展以休闲养生、文化体验、旅游度假为特色的“医疗+养生+康复+旅游”产品，建设与田园风情、山水生态、休闲旅游相结合的养生体验和疗养基地，打造休闲康养旅游集散地。"},
]
k_chengche = [
    {"type": "title", "text": "乘车安排"},
    {"type": "left", "text": "一、时间"},
    {"type": "text", "text": "10月23日下午14:00准时出发"},
    {"type": "left", "text": "二、内容"},
    {"type": "text", "text": "嘉宾由沽源县库伦淖尔旅游度假区开元酒店前门集体乘车赴沽源县北麦生态农业有限公司"},
    {"type": "left", "text": "三、乘客"},
    {"type": "text", "text": "联通雄安产业互联网有限公司专家 "},
    {"type": "text", "text": "北京启明星辰信息安全技术有限公司 "},
    {"type": "text", "text": "浙江大华技术股份有限公司专家"},
    {"type": "text", "text": "有关金融机构及院校"},
    {"type": "text", "text": "张家口市工信局主要负责人"},
    {"type": "text", "text": "沽源县商务局主要负责人"},
    {"type": "text", "text": "塞北管理区发展和改革局主要负责人"},
    {"type": "text", "text": "沽源县联通主要负责人"},
    {"type": "left", "text": "四、引导车"},
    {"type": "text", "text": "冀G 31107 "},
    {"type": "left", "text": "五、联络员"},
    {"type": "text", "text": "常昊宇 18603233291"},
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

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
k_title_city = "（经开区站）"
k_title_sub = "百城千园行-经开区站"
k_local = "张家口市经开区联通大楼六楼多功能会议室"
k_elocal = "张家口国际大酒店一楼"
k_zuowei = "../static/座位表.jpg"
k_time = [
    {"type": "main", "text": "9月21日-上午"},
    {"time":"08:00-09:00", "text":"张家口市经开区联通大楼六楼多功能会议室报道"},
    {"time":"09:00-09:05", "text":"主持人介绍与会领导和嘉宾"},
    {"time":"09:05-09:10", "text":"经开区管委会分管领导致辞"},
    {"time":"09:10-09:15", "text":"中国联合网络通信有限公司张家口市分公司副总经理致辞"},
    {"time":"09:15-09:35", "text":"市工业和信息化局分管领导致辞"},
    {"time":"09:35-09:55", "text":"企业如何实现数字化转型"},
    {"time":"09:55-10:10", "text":"工赋园区、数智未来-锐捷网络带你迈向智能制造"},
    {"time":"10:10-10:25", "text":"工业数字化转型安全实践"},
    {"time":"10:25-10:30", "text":"签约仪式"},
    {"time":"10:30-10:40", "text":"茶歇及观展"},
    {"time":"10:40-11:00", "text":"河北北方铸业有限公司就信息化建设进行分享"},
    {"time":"11:00-11:05", "text":"华夏银行张家口分行做“数字贷”产品推介"},
    {"time":"11:05-11:10", "text":"中信银行张家口分行做“数字贷”产品推介"},
    {"time":"11:10-11:20", "text":"中国银行张家口分行做数字人民币应用推介"},
    {"time":"11:20-12:00", "text":"自由对接"},
    {"time":"12:00", "text":"就餐"},
]
k_xuzhi = [
    {"type": "title", "text": "会议须知"},
    {"type": "text", "text": "您好!欢迎您来参加工业互联网一体化进园区进企业“百城千园行”活动暨企业数字化转型发展推进行动 (经开区站)，为确保会议的顺利进行，请您关注以下事项。"},
    {"type": "left", "text": "一、严格遵守会议纪律"},
    {"type": "text", "text": "1、会议开始后，请将手机关闭或置于静音状态，保持会场安静，不得在会场内接打电话，不得随意走动。"},
    {"type": "text", "text": "2、会场内请勿吸烟，保持会场清洁。"},
    {"type": "text", "text": "3、会场内摄像、录音统一由会务组安排"},
    {"type": "text", "text": "4、与会人员会议期间如需帮助请与会务组联系，会务人员联系方式如下"},
    {"type": "text", "text": "会务经理: 朱广乐18603237014"},
    {"type": "text", "text": "酒店经理: 李经理18832397658"},
    {"type": "left", "text": "二、会议时间和地点"},
    {"type": "text", "text": "1、会议时间:"},
    {"type": "text", "text": "2023年9月21日（星期四）:"},
    {"type": "text", "text": "2、会议地点:"},
    {"type": "text", "text": "张家口市经开区联通大楼六楼多功能会议室（河北省张家口市高新区敬业街）"},
    {"type": "text", "text": "3、就餐地点:"},
    {"type": "text", "text": "张家口国际大酒店一楼"},
]
k_jianjie = [
    {"type": "title", "text": "张家口经开区简介"},
    {"type": "text", "text": "张家口市位于河北省西北部，地处京、冀、晋、蒙四省通衢之地，距北京180公里，距天津港340公里，是沟通中原与北疆、连接环渤海经济圈和西北内陆资源区的重要节点。张家口市有19个县区，经开区既是开发区也是主城区，托四镇两街，面积148平方公里，辖38个行政村村、14个社区、1个国营农场，常驻人口38万。"},
    {"type": "text", "text": "作为开发区，经开区拥有东山产业园区、现代产业园区等多个个产业园区，重点培育了“新能源、生物科技、楼宇经济、现代服务、文体旅游康养”五大产业，驻有金风科技、天津中环、神威制药等一批国内外知名企业。近年来，全区主导产业收入连续呈两位数增长，近期有望得到国务院批复，晋升为国家级开发区。作为主城区，市委、市政府和市直部门在这里办公，北方学院、建工学院、张家口技师学院、张家口职业技术学院4所大专院校坐落在这里，市博物馆、档案馆、图书馆、规划馆、地质博物馆、文化会展中心、奥体中心等文体场馆坐落在这里；经开区已经成为全市政治、文化、教育的中心。"},
    {"type": "text", "text": "当前，经开区正处于战略机遇叠加、优势集中释放的黄金发展期，具备了向更高层级迈进的基础条件。经开区发展面临着三大机遇：一是北京携手张家口举办2022年冬奥会。2022年冬奥会雪上项目的主赛场是崇礼区，经开区作城市中心区同样也是冬奥会的重要接待服务区，在国际奥委会和国家、省、市支持下，短时间内将建设一批世界级的配套设施，在多个层面享受项目、资金、政策等支持。在京张高铁通车后，将成为联接北京与崇礼两个比赛场馆的的重要中转站和交通枢纽，与北京同城化的优势明显。二是张家口建设可再生能源示范区。国家通过张家口建设可再生能源示范区规划，张家口市可再生能源示范区规划明确，五个核心功能区中的可再生能源创新城、可再生能源综合商务区、高端装备制造区将在经开区建设，有利于充分享受国家财政补贴、税收优惠、用地倾斜政策，加快发展可再生能源、智能电网、新能源汽车、新材料、现代服务业等新兴产业。三是京津冀协同发展。我区区位优越、交通便捷，已经构筑起纵横交错、四通八达的现代化立体交通网。打造了“一区多园”多个项目建设平台，有效提升了产业承载能力。同时，我区处于京津冀协同发展一核、双城、三轴、四区、多节点的主轴线上，有利于在京津冀协同发展大势中承接产业转移和接受政策辐射。"},
    {"type": "text", "text": "经开区发展具有五大优势：一是区位条件独特。位于张家口市的中心城区，城市四周被南山、西山、东山、望山等产业园区环绕，是主城区服务、辐射周边产业园区的核心节点。二是交通畅通便捷。城市核心区距宁远机场仅9公里，已经开通到成都、哈尔滨、厦门、上海等一线城市的直达航班；高铁站位于全区中心区域，是我国北方东西大动脉上的重要枢纽。三是发展空间广阔。城市规划范围内可开发用地面积近70平方公里，包括15平方公里的高铁以南区域和38.9平方公里的洋河新区，特别是沙岭子镇、东山产业园的划归，进一步拓宽了城市发展空间。四是生态环境良好。辖区内有清水河和洋河以及多个大型人工湖和主题公园，规划实施了占地3000亩的森林公园、太子山和凤凰山山体公园等生态绿化工程，是市区生态环境最好的区域。五是行政服务便捷高效。经开区是河北省唯一具有市级行政管理权限的开发区，在全市率先成立行政审批局，开启了“一枚印章管审批，审批不见面，最多跑一次”的“绿色通道”。作为全市综合改革试点，“网上政府、身边政府”和城市规划建设管理运营等一批改革在我区先行先试，为推动发展释放更多红利，营造了良好的营商环境。"}
]
k_chengche = [
    {"type": "title", "text": "乘车安排"},
    {"type": "left", "text": "一、时间"},
    {"type": "text", "text": "&&&&&&&&&&&&&&&&"},
    {"type": "left", "text": "二、内容"},
    {"type": "text", "text": "巴拉巴拉"},
    {"type": "left", "text": "三、乘客"},
    {"type": "text", "text": "555555555555122412412"},
    {"type": "text", "text": "51251235"},
    {"type": "text", "text": "535135"},
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
    with open("app/static/座位表.jpg", 'r') as img_f:
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

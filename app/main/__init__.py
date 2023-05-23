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

@b.route("/MP_verify_TTH4vMTo8zLwTLXd.txt", methods=["GET"])
def wxyanzheng():
    return render_template("MP_verify_TTH4vMTo8zLwTLXd.txt")

@b.route("/", methods=["GET"])
@b.route("/index", methods=["GET"])
def index():
    return render_template("index.html")


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
    print(number)
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

@b.route("/timeanpai", methods=["GET"])
def timeanpai():
    return render_template("timeanpai.html")

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
    print(data)
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










@b.route("/admin", methods=["GET"])
@login_required
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

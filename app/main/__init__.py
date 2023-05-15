# -*- coding: utf-8 -*-
"""
@Author:waiwen
@Time: 2020/5/13 14:27
@Email: iwaiwen@163.com
@Software: PyCharm
@File    : __init__.py.py
"""
import json
import pickle
from database_mongo import getdb, getdb_user
import requests

from flask import render_template, jsonify
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
    return render_template("index_wx.html")

@b.route("/index_nowx", methods=["GET"])
def index_wx():
    return render_template("index.html")

@b.route("/signin_ok", methods=["GET"])
def signin_ok():
    return render_template("signin.html")


@b.route("/signin/<openid>", methods=["Get"])
def signin(openid):
    db = getdb_user()
    data = db.find_one({"openid": openid})
    db.close()
    name = data['name']
    phone = data['phone']
    print(data)
    # insert
    db2 = getdb()
    db2.insert_one({
        "openid": openid,
        "time": time.time(),
    })
    db2.close()
    # print
    kwargs = {
        "name": name,
        "phone": phone,
    }
    return render_template("signin.html", **kwargs)

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

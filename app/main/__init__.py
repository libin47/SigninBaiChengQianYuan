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
from database_mongo import getdb

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



@b.route("/", methods=["GET"])
@b.route("/index", methods=["GET"])
def index():
    return render_template("index.html")

@b.route("/index_wx", methods=["GET"])
def index_wx():
    return render_template("index_wx.html")
@b.route("/signin_ok", methods=["GET"])
def signin_ok():
    return render_template("signin.html")
@b.route("/signin", methods=["POST"])
def signin():
    d = json.loads(request.get_data(as_text=True))
    name = str(d["name"])
    phone = int(d.get("phone"))
    danwei = str(d["danwei"])
    times = time.localtime()
    db = getdb()
    db.insert_one({
        "name": name,
        "phone": phone,
        "danwei": danwei,
        "time": times,
    })
    return jsonify({"ok": True})













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

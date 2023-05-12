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

from flask import render_template, jsonify
from flask import Blueprint, request, redirect, url_for, flash, send_file
from flask_login import login_user, login_required, logout_user
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Length, DataRequired, Optional
from flask_wtf.form import FlaskForm
from flask_login import LoginManager

# from GaoKao2022 import predict, get_batch_info, predict_college, update_province_data, get_province_log, \
#     get_split_cwb, start_all_data, start_province, get_province_stat, restart_table, update_all, restart_rule, \
#     del_province, reset_table, get_school_rank, reset_redis, download_school_rank
# from GaoKao2022.SQL.setting import AuthINFO

from app.auth.auth import Auth
import tracemalloc
import time

b = Blueprint("main", __name__)



@b.route("/", methods=["GET"])
@b.route("/index", methods=["GET"])
@login_required
def index():
    return render_template("index.html")


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
# from GaoKao2020.settings import env, TOKEN


@login_manager.user_loader
def load_user(id):
    return Auth(id=1, username=AuthINFO.get("username"), password=AuthINFO.get("password"))


@b.route("/findCollege", methods=["POST"])
def find_colleges():
    """
    :return:
    """
    d = json.loads(request.get_data(as_text=True))
    # 检测token
    token = d.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    # 读取参数
    province_id = int(d["province_id"])
    wenli = int(d.get("wenli"))
    score = int(d["score"])
    rank = int(d.get("rank"))
    batch_text = {
        'batch_norm': d.get("batch_text", ""),
        'batch_plan': d.get("batch_plan", ""),
        'batch_fsx': d.get("batch_fsx", "")
    }
    # 筛选
    select_list = {
        'college_id': int(d.get("college_id", -1)),
        'city_id': d.get("city_id", []),
        'major_code_2': d.get("major_code_2", []),
        'nature_code': d.get("nature_code", []),
        'first_code': d.get("first_code", []),
        'type_code': d.get("type_code", []),
        'demand': d.get("demand", []),
        'keyword': str(d.get("query", "")),
        'sg_name': str(d.get("sg_name", ""))
    }
    # 可选参数
    detail = d.get("detail", False)
    college_province = d.get("college_province", False)

    # 检测参数
    if (province_id>30) or (province_id<1):
        return jsonify({"errmsg": "province_id error", "code": -2})
    if (rank<0) or (score<0):
        return jsonify({"errmsg": "score or rank error", "code": -3})
    a = time.time()
    df = predict(province_id, wenli, batch_text, score, rank, select_list, detail, college_province)
    print(time.time()-a)
    return jsonify(df)


@b.route("/createXlsx", methods=["GET"])
def create_xlsx():
    province_id = int(request.args.get("province_id"))
    msg = get_school_rank(province_id)
    return jsonify(msg)


@b.route("/downloadXlxs", methods=["GET"])
def download_file():
    province_id = int(request.args.get("province_id"))

    filename = download_school_rank(province_id)
    if filename['ok']:
        return send_file(filename['filename'],
                         as_attachment=True,
                         attachment_filename='%s.xlsx'%(province_id),
                         cache_timeout=0)
    else:
        return "可能需要先生成!"


@b.route("/<string:filename>", methods=["GET"])
def download_file_name(filename):
    if filename:
        return send_file('xlsx/'+filename, attachment_filename=filename)
    return 'error', 400


# 获取批次之间的关联信息
@b.route("/findBatchInfo", methods=["POST"])
def find_batch_info():
    """
    :return:
    """
    d = json.loads(request.get_data(as_text=True))
    token = d.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    # 读取参数
    province_id = int(d["province_id"])
    batch_data = get_batch_info(province_id)
    return jsonify(batch_data)


# 获取院校概率
@b.route("/findCollegeProb", methods=["POST"])
def find_college_prob():
    d = json.loads(request.get_data(as_text=True))
    # 检测token
    token = d.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    # 读取参数
    province_id = int(d["province_id"])
    wenli = int(d.get("wenli"))
    score = int(d["score"])
    rank = int(d.get("rank"))
    college_id = int(d.get("college_id"))
    batch_text = {
        'batch_norm': d.get("batch_text", ""),
        'batch_plan': d.get("batch_plan", ""),
        'batch_fsx': d.get("batch_fsx", "")
    }
    # 检测参数
    if (province_id>30) or (province_id<1):
        return jsonify({"errmsg": "province_id error", "code": -2})
    if (rank<0) or (score<0):
        return jsonify({"errmsg": "score or rank error", "code": -3})
    df = predict_college(province_id, wenli, batch_text, score, rank, college_id)
    return jsonify(df)


# 更新省份
@b.route("/updateProvince", methods=["POST"])
def update_province():
    d = json.loads(request.get_data(as_text=True))
    token = d.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    province_id = int(d["province_id"])
    msg = update_province_data(province_id)
    return jsonify(msg)


# 更新省份
@b.route("/updateAll", methods=["POST"])
def update_all_province():
    d = json.loads(request.get_data(as_text=True))
    token = d.get("token", "")
    top = int(d.get("top", 1))
    end = int(d.get("end", 30))
    province_list = d.get("province_list", [])
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    msg = update_all(top, end, province_list)
    return jsonify(msg)


# 启动省份
@b.route("/startAll", methods=["POST"])
def restart_all():
    d = json.loads(request.get_data(as_text=True))
    token = d.get("token", "")
    top = int(d.get("top", 1))
    end = int(d.get("end", 30))
    replace = bool(d.get("replace", False))
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    start_all_data(top, end, replace)
    return "OK!"


@b.route("/startProvince", methods=["POST"])
def restart_province():
    d = json.loads(request.get_data(as_text=True))
    token = d.get("token", "")
    province = d.get("province_id")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    start_province(province)
    return "OK!"


# 获取日志
@b.route("/findLogProvince", methods=["POST"])
def find_log_province():
    d = json.loads(request.get_data(as_text=True))
    token = d.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    province_id = d["province_id"]
    msg = get_province_log(province_id)
    return jsonify(msg)


# 获取日志-文件中
@b.route("/findLogProvinceFile", methods=["POST"])
def find_log_province_infile():
    d = json.loads(request.get_data(as_text=True))
    token = d.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    province_id = d["province_id"]
    msg = get_province_log(province_id, True)
    return jsonify(msg)


# 获取状态
@b.route("/findProvinceStat", methods=["GET"])
def find_stat_province():
    token = request.args.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    msg = get_province_stat(0)
    return jsonify(msg)


# 获取冲稳保的划分条件
@b.route("/findSplit", methods=["GET"])
def find_split():
    msg = get_split_cwb()
    return jsonify(msg)


# 先进行校验再进入到主界面
@b.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember_me = form.remember_me.data
        if username == AuthINFO.get("username") and password == AuthINFO.get("password"):
            login_user(user=Auth(id=1, username=username, password=password), remember=remember_me)
            return redirect(url_for("main.index"))
        else:
            flash("登录失败！请检查用户名和密码！")
            return render_template("login.html", formid="loginForm", action="/login", method="post", form=form)
    return render_template("login.html", formid="loginForm", action="/login", method="post", form=form)



tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()


@b.route("/get-info", methods=["GET"])
def getinfo():
    snapshot2 = tracemalloc.take_snapshot()
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    print(top_stats)
    return jsonify({"code": 1, "msg": "success"})


# 退出登录
@b.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@b.route("/readiness", methods=["GET"])
@b.route("/liveness", methods=["GET"])
def probe():
    return "ok"


# 删除表格重来
@b.route("/delProvinceTable", methods=["POST"])
def delprovincetable():
    d = json.loads(request.get_data(as_text=True))
    token = d.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    province_id = int(d["province_id"])
    msg = del_province(province_id)
    return jsonify(msg)


# 删除表格重来
@b.route("/deltable", methods=["POST"])
def del_tables():
    token = request.args.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    msg = restart_table()
    return jsonify(msg)


# 删除rule表格
@b.route("/delRuleTable", methods=["POST"])
def del_rule_tables():
    token = request.args.get("token", "")
    if env == "prod" and token != TOKEN:
        return jsonify({"errmsg": "token error", "code": -1})
    msg = restart_rule()
    return jsonify(msg)


# 重设表格字段类型
@b.route("/resetTable", methods=["POST"])
def resettable():
    msg = reset_table()
    return jsonify(msg)


# 重设表格字段类型
@b.route("/clearRedis", methods=["POST"])
def clear_redis():
    msg = reset_redis()
    return jsonify(msg)
# -*- coding: utf-8 -*-
"""
@Author:waiwen
@Time: 2020/5/13 14:25
@Email: iwaiwen@163.com
@Software: PyCharm
@File    : __init__.py.py
"""
from flask import Flask

from config import config
from app.main import b as main_b


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.register_blueprint(main_b)
    return app

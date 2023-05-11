# -*- coding: utf-8 -*-
import os

env = os.environ.get("ENV")

if env == "prod":
    MYSQL_CONFIG = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB"),
    }
    AuthINFO = {
        "username": os.environ.get("USERNAME"),
        "password": os.environ.get("PASSWORD")
    }

    TOKEN = os.environ.get("TOKEN")
# 连接本地数据库
else:
    MYSQL_CONFIG_OLD = {
        'host': "192.168.101.101",
        'port': 3305,
        'user': "lwb",
        'password': "lwb2010",
        'database': "enrollment",
        'auth_plugin':'mysql_native_password'
    }
    MYSQL_CONFIG = {
        'host': "192.168.100.200",
        'port': 3306,
        'user': "lwb",
        'password': "lwb2010",
        'database': "gkzy_dealing_data_ly",
        'auth_plugin': 'mysql_native_password'
    }
    AuthINFO = {
        "username": "waiwen",
        "password": "1234567"
    }
    TOKEN = os.environ.get("token", "qwer1234")
# -*- coding: utf-8 -*-
import os
# 本地默认值
# redis
RedisIP = 'localhost'
RedisPort = 6379
RedisPassWord = ''
RedisBATCH = 0
RedisBATCHALL = 6
RedisINIT = 1
RedisUPDATE = 2
RedisDF = 3
RedisCONFIG = 4
RedisSUCCESS = 5
# 院校招生计划
SQLPlanSchool = {
        'host': "192.168.100.200",
        'port': 3306,
        'user': "lwb",
        'password': "lwb2010",
        'database': "gkzy_dealing_data_ly",
        'auth_plugin': 'mysql_native_password'
    }
TablePlanSchool = "ga_zy_college_plan"
# 专业招生计划
SQLPlanSp = SQLPlanSchool
TablePlanSp = "ga_zy_specialplan"
# 院校分数线
SQLDataSchool = SQLPlanSchool
TableDataSchool = "ga_zy_fsx_xx"
# 专业分数线
SQLDataSp = SQLPlanSchool
TableDataSp = "ga_zy_fsx_zy"
# 一分一段表
SQLFsd = SQLPlanSchool
TableFsd = "ga_zy_fsd"
# 批次线
SQLFsx = SQLPlanSchool
TableFsx = "ga_zy_fsx_sf"
# 院校信息
SQLInfo = SQLPlanSchool
TableInfo = "ga_zy_college"
# city
SQLCity = SQLPlanSchool
TableCity = "ga_city"
# major
SQLMajor = SQLPlanSchool
TableMajor = "ga_zy_major"
# 写入的表
SQLGoal = {
        'host': "192.168.100.200",
        'port': 3306,
        'user': "lwb",
        'password': "lwb2010",
        'database': "gkztc_admin2",
        'auth_plugin': 'mysql_native_password'
    }
TableGoalRule = 'algorithm_province_rule'
TableGoalSchool = 'algorithm_zy_school'
TableGoalSp = 'algorithm_zy_sp'
# 账号密码token
AuthINFO = {
    "username": "waiwen",
    "password": "1234567"
}
TOKEN = os.environ.get("token", "qwer1234")


env = os.environ.get("ENV")
# 正式数据库
if env in ["prod", "dev"]:
    MYSQLdb = os.environ.get("MYSQL_DB")
    SQLPlanSchool = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_PLANSCHOOL", MYSQLdb),
    }
    TablePlanSchool = os.environ.get("TABLE_PLANSCHOOL", "ga_zy_college_plan")

    SQLPlanSp = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_PLANSP", MYSQLdb),
    }
    TablePlanSp = os.environ.get("TABLE_PLANSP", "ga_zy_specialplan")

    SQLDataSchool = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_DATASCHOOL", MYSQLdb),
    }
    TableDataSchool = os.environ.get("TABLE_DATASCHOOL","ga_zy_fsx_xx")

    SQLDataSp = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_DATASP", MYSQLdb),
    }
    TableDataSp = os.environ.get("TABLE_DATASP", "ga_zy_fsx_zy")

    SQLFsx = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_FSX", MYSQLdb),
    }
    TableFsx = os.environ.get("TABLE_FSX", "ga_zy_fsx_sf")

    SQLFsd = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_FSD", MYSQLdb),
    }
    TableFsd = os.environ.get("TABLE_FSD", "ga_zy_fsd")

    SQLInfo = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_INFO", MYSQLdb),
    }
    TableInfo = os.environ.get("TABLE_INFO", "ga_zy_college")

    SQLCity = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_CITY", MYSQLdb),
    }
    TableCity = os.environ.get("TABLE_CITY", "ga_city")

    SQLMajor = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_MAJOR", MYSQLdb),
    }
    TableMajor = os.environ.get("TABLE_MAJOR", "ga_zy_major")

    # 登录信息
    AuthINFO = {
        "username": os.environ.get("USERNAME"),
        "password": os.environ.get("PASSWORD")
    }
    TOKEN = os.environ.get("TOKEN")

    SQLGoal = {
        'host': os.environ.get("MYSQL_HOST"),
        'port': os.environ.get("MYSQL_PORT"),
        'user': os.environ.get("MYSQL_USER"),
        'password': os.environ.get("MYSQL_PASSWORD"),
        'database': os.environ.get("MYSQL_DB_GOAL", MYSQLdb),
    }
    TableGoalRule =os.environ.get("TABLE_GOAL_RULE", TableGoalRule)
    TableGoalSchool = os.environ.get("TABLE_GOAL_SCHOOL", TableGoalSchool)
    TableGoalSp = os.environ.get("TABLE_GOAL_SP", TableGoalSp)

    RedisIP = os.environ.get("REDIS_IP")
    RedisPort = os.environ.get("REDIS_PORT")
    RedisPassWord = os.environ.get("REDIS_PASS")

    RedisBATCH = os.environ.get("REDIS_1")
    RedisBATCHALL = os.environ.get("REDIS_2")
    RedisINIT = os.environ.get("REDIS_3")
    RedisUPDATE = os.environ.get("REDIS_4")
    RedisDF = os.environ.get("REDIS_5")
    RedisCONFIG = os.environ.get("REDIS_6")
    RedisSUCCESS = os.environ.get("REDIS_7")



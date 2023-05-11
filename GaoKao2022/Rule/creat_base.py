# -*- coding: utf-8 -*-
from ..SQL.setting import SQLGoal, TableGoalRule
from ..SQL.sql_util import get_connect
import pandas as pd
from mysql.connector import connect


# 检查目标库中是否存在该表格
def check_tables():
    db = connect(**SQLGoal)
    sql_text = "show tables"
    df = pd.read_sql(sql_text, db)
    # df.to_excel()
    db.close()
    if TableGoalRule in df.transpose().values:
        return True
    else:
        return False


# 以初始化数据初始化表格
def init_data():
    con = get_connect(SQLGoal)
    df_rule = pd.read_csv('GaoKao2022/Rule/data/province_rule_base.csv',sep='|')
    df_rule.to_sql(TableGoalRule, con=con, if_exists='replace', index=False)
    return True
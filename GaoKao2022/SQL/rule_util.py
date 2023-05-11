# -*- coding: utf-8 -*-
from .setting import SQLGoal, TableGoalRule
from mysql.connector import connect
import pandas as pd

config = {
    "year_old": 3,      # 使用的最近3年的历史数据
    "years": 2022,      # 今年时2022年
    "wenli_year": 2     # 对于文理是0的省份，最近两年文理都是0(19年开始出现文理1和2的)
}

varchar_length = {
    'strs': 64,         # base中标明strs类型的字段varchar长度
    'str': 512          # base中标明str类型的字段的varchar长度
}


# 获取该省份的招生规则
def get_rule(province_id):
    db = connect(**SQLGoal)
    sql_text = "SELECT * FROM %s WHERE province_id=%s AND stat=1"%(TableGoalRule, province_id)
    df = pd.read_sql(sql_text, db)
    batch = list(set(df.batch_text))
    batch.sort()
    db.close()
    assert len(df) == len(batch), "该省份规则错误，检查数据"
    return df, batch


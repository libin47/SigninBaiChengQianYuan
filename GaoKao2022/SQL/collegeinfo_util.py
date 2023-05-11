# -*- coding: utf-8 -*-
from .base import *
from ..Util.province_id import id2province, id2nature
import pandas as pd


def get_college_info():
    sql_text = """
        SELECT distinct id as college_id, schoolnature, f211, f985, firstrate, province_id, city_id, typecode
        FROM %s
        WHERE stat=1
    """%TableInfo
    df_info = pd.read_sql(sql_text, connect(**SQLInfo))
    # province
    df_info['college_province'] = df_info.province_id.apply(lambda x:id2province(x))
    df_info.rename({"province_id":"college_province_id"}, axis=1, inplace=True)
    # nature
    df_info['nature_text'] = df_info.schoolnature.apply(lambda x:id2nature(x))
    # city
    city_text = """
        select id as city_id, name as city
        from %s
    """%TableCity
    city = pd.read_sql(city_text, connect(**SQLCity))
    df_info = pd.merge(df_info, city, on=["city_id"], how="left")
    df_info['city'] = df_info.city.apply(lambda x: "未知" if pd.isnull(x) else x)
    df_info['city'] = df_info['city'].apply(lambda x: x[:-1] if x[-1] == "市" else x)
    # columns: college_id, schoolnature, nature_text, f211, f985, firstrate, college_province_id, college_province, city_id, city, typecode
    return df_info


def merge_college_info(cfg, df, log):
    info = get_college_info()
    df = pd.merge(df, info, on='college_id', how='left')
    return df
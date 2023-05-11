# -*- coding: utf-8 -*-
from .base import *
import pandas as pd


# 根据分数获取排名
def get_score_rank(fsd, score, wenli):
    df = fsd[fsd.wenli==wenli]
    if len(df)==0:
        return -1

    df_s = df[df.score==score]
    if len(df_s)>0:
        return df_s.iloc[0]['rank']

    index = sum(score < df['score'])
    if index>=len(df):
        index = len(df) - 1
    rank = df.iloc[index]['rank']
    return rank


# 获取一分一段表
def get_fsd(province_id, years, zhongzhi):
    db, table, _ = select_db_table('fsd')
    sql_text = """
        SELECT wenli, line score, `rank`
        FROM {table}
        WHERE years={year} AND province_id={province} AND cengci={zhongzhi} AND gk_period=1 AND 
              category like "普通类" AND stat=1
    """.format(table=table,
               year=years,
               province=province_id,
               zhongzhi=zhongzhi+1)
    fsd = pd.read_sql(sql_text, db)
    db.close()

    fsd = fsd.sort_values(by=['score'], ascending=False, axis=0, inplace=False)
    return fsd


# 获取批次线 排名
def get_sf_rank(sfscore, province_id, years, zhongzhi):
    if len(sfscore)==0:
        sfscore['batch_rank'] = -1
        return sfscore
    fsd = get_fsd(province_id, years, zhongzhi)
    sfscore['batch_rank'] = sfscore.apply(lambda x: get_score_rank(fsd, x['batch_score'], x['wenli']), axis=1)
    return sfscore


# 获取批次线 分数
def get_sf_score(province_id, years, batch_text):
    db, table, wheretxt = select_db_table('fsx')
    sql_text = """
        SELECT wenli, MAX(score) batch_score
        FROM {table}
        WHERE years={year} AND province_id={province} AND batch_text="{batchtext}" AND {where}
        GROUP BY wenli, batch_text
    """.format(table=table,
               year=years,
               province=province_id,
               batchtext=batch_text,
               where=wheretxt)
    df = pd.read_sql(sql_text, db)
    db.close()
    return df


# 获取批次线和对应的排名
def get_sf(cfg, years, batch_text, log):
    sf_score = get_sf_score(cfg['province_id'], years, batch_text)
    sf_rank = get_sf_rank(sf_score, cfg['province_id'], years, cfg['gaozhi'])
    log.info("★[批次线:%s]★ %s条" % (years, len(sf_score)))
    # wenli, batch_score, batch_rank
    return sf_rank

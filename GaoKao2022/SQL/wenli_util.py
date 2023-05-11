# -*- coding: utf-8 -*-
from .base import select_db_table
from .rule_util import config
import pandas as pd


# 获取这一年的wenli
def get_wenli_data(province_id, years, wenlitype, mode, log, cfg):
    db, table, wheretxt = select_db_table(mode, False, province_id)
    batchlist = str(tuple(cfg['data_batch_%s'%years])).replace(',)', ')')

    sql_text = "SELECT wenli FROM %s WHERE years=%s AND batch_text in %s AND province_id=%s AND %s GROUP BY wenli"\
               %(table, years, batchlist, province_id, wheretxt)
    batch = pd.read_sql(sql_text, db)
    db.close()
    # if len(batch)>2:
    #     log.debug("☟[%s年wenli]种类大于2:%s，可能因此触发异常" % (years, list(batch.wenli)))
    wenlilist = list(set(batch.wenli))
    wenlilist.sort()
    result = []
    if wenlitype==0:
        if 0 in wenlilist:
            result.extend([0])
        if 1 in wenlilist and 2 in wenlilist:
            result.extend([1, 2])
    elif wenlitype==212:
        if 1 in wenlilist and 2 in wenlilist:
            result = [1, 2]
        if 21 in wenlilist and 22 in wenlilist:
            result = [21, 22]
    elif wenlitype==12:
        if 1 in wenlilist and 2 in wenlilist:
            result = [1, 2]

    log.info("★[%s]★%s -> %s"%(years, wenlilist, result))
    return result


# 获取历年的文理规则
def get_wenli_true(province_id, dict_batch, log):
    wenlitype, mode, years = dict_batch['wenli'], dict_batch['mode'], dict_batch['years']
    if wenlitype==12:
        dict_batch['goal_wenli'] = [1, 2]
        for i in range(config['year_old']):
            year = years - i - 1
            dict_batch['data_wenli_%s'%year] = [1, 2]
            dict_batch['data_ts_wenli_%s'%year] = 'keep'
    if wenlitype==212:
        dict_batch['goal_wenli'] = [21, 22]
        for i in range(config['year_old']):
            year = years - i - 1
            dict_batch['data_wenli_%s'%year] = get_wenli_data(province_id, year, wenlitype, mode, log, dict_batch)
            if dict_batch['data_wenli_%s'%year]==[1, 2]:
                dict_batch['data_ts_wenli_%s' % year] = 'trans'
            elif len(dict_batch['data_wenli_%s' % year]) == 0:
                dict_batch['data_ts_wenli_%s' % year] = ''
            else:
                dict_batch['data_ts_wenli_%s' % year] = 'keep'
    if wenlitype==0:
        dict_batch['goal_wenli'] = [0]
        for i in range(config['year_old']):
            year = years - i - 1
            dict_batch['data_wenli_%s'%year] = get_wenli_data(province_id, year, wenlitype, mode, log, dict_batch)
            if dict_batch['data_wenli_%s'%year]==[0]:
                dict_batch['data_ts_wenli_%s' % year] = 'keep'
            elif len(dict_batch['data_wenli_%s'%year])==0:
                dict_batch['data_ts_wenli_%s' % year] = ''
            else:
                dict_batch['data_ts_wenli_%s' % year] = 'cos'
    return dict_batch
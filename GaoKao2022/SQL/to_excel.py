import os
import time
import pandas as pd
from .sf_util import get_fsd
from .rule_util import config as cfg_sys


def get_rank_score(fsd, rank, wenli):
    if rank==-1:
        return -1
    df = fsd[fsd.wenli==wenli]
    if len(df)==0:
        return -1

    df_s = df[df['rank']==rank]
    if len(df_s)>0:
        return df_s.iloc[0]['score']

    index = sum(rank > df['rank'])
    if index>=len(df):
        index = len(df) - 1
    score = df.iloc[index]['score']
    return score


def df2excel_subwenli(df, df_fsd, wenli, df_fsd_old, old_year):
    df = df.groupby(['college_id']).agg({'college_id':'min', 'schoolname':'min',
                                         'minscore_rank_%s'%old_year:'max',
                                         'predict_rank':'max'})
    df['predict_rank'] = df['predict_rank'].astype('int')
    df['minscore_%s'%old_year] = df.apply(lambda x: get_rank_score(df_fsd_old, x['minscore_rank_%s'%old_year], wenli), axis=1)
    df['predict_score'] = df.apply(lambda x: get_rank_score(df_fsd, x['predict_rank'], wenli), axis=1)
    df = df[['college_id', 'schoolname', 'minscore_rank_%s'%old_year, 'minscore_%s'%old_year, 'predict_rank', 'predict_score']]
    df = df.rename({'schoolname': '院校', 'minscore_rank_%s'%old_year: '%s排位'%old_year,
                    'minscore_%s'%old_year:'%s分数'%old_year, 'predict_rank': '预测排位',
                    'predict_score':'预测分数'}, axis=1)
    return df


def get_wenli_list(wenli):
    if wenli==12:
        return [1,2]
    elif wenli==212:
        return [21, 22]
    elif wenli==0:
        return [0]

def get_wenli_name(wenli):
    if wenli==0:
        return '综合'
    if wenli==1:
        return '文科'
    if wenli==2:
        return '理科'
    if wenli==21:
        return '历史'
    if wenli==22:
        return '物理'
    return '未知文理'


def df2excel(data):
    result = {}
    for batch in data.keys():
        df = data[batch]['data']
        config = data[batch]['cfg']
        wenli_list = get_wenli_list(config['wenli'])
        old_year = cfg_sys['years'] - 1

        df_fsd = get_fsd(config['province_id'], config['goal_years'], 0)
        df_fsd_old = get_fsd(config['province_id'], old_year, 0)

        for wenli in wenli_list:
            df_sub = df[df.wenli == wenli]
            df_result = df2excel_subwenli(df_sub, df_fsd, wenli, df_fsd_old, old_year)
            result[batch+get_wenli_name(wenli)] = df_result
    return result


def download_excel(result):
    try:
        os.mkdir('app/xlsx/')
    except:
        pass
    filename = 'app/xlsx/%s.xlsx'%(int(time.time()*1000000))
    file = pd.ExcelWriter(filename)
    for batch in result.keys():
        df = result[batch]
        df.to_excel(file, sheet_name=batch, index=False)
    file.close()
    return filename[4:]

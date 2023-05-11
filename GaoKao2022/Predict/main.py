# -*- coding: utf-8 -*-
from ..SQL.base import prob_cols
from ..PredictProb2022 import probability
from ..SQL.demand_util import demand_jg
from ..SQL.sql_util import get_data_by_id
import pandas as pd



split_c = 0.15
split_cw = 0.7
split_wb = 0.97


# 预测概率
def predict_prob(cfg, df, wenli, score, rank, select_list, detail, college_province):
    province_id = int(cfg['province_id'])
    pcls = prob_cols.copy()
    # wenli
    df = df[df.wenli==wenli]
    # keyword
    if ('keyword' in select_list.keys()) and len(select_list['keyword'])>0:
        keyword = select_list['keyword']
        if cfg['mode'] in ['sp', 'group']:
            df = df[df.schoolname.str.contains(keyword)|df.sp_name.str.contains(keyword)]
        else:
            df = df[df.schoolname.str.contains(keyword)]
    # sg_name
    detail_group = True
    if ('sg_name' in select_list.keys()) and (cfg['mode'] == 'group'):
        sg_name = select_list['sg_name']
        if len(sg_name)>0:
            detail_group = False
            df = df[df.sg_name==sg_name]
    # city
    if ('city_id' in select_list.keys()) and (len(select_list['city_id'])>0):
        city_id = select_list['city_id']
        df = df[df.city_id.isin(city_id)]
    # college_id
    if ('college_id' in select_list.keys()) and (select_list['college_id']>0):
        df = df[df.college_id==select_list['college_id']]
    # nature_code
    if ('nature_code' in select_list.keys()) and (len(select_list['nature_code'])>0):
        df = df[df.schoolnature.isin(select_list['nature_code'])]
    # type_code
    if ('type_code' in select_list.keys()) and (len(select_list['type_code'])>0):
        df = df[df.typecode.isin(select_list['type_code'])]
    # first_code
    if ('first_code' in select_list.keys()) and (len(select_list['first_code'])>0):
        first_code = select_list['first_code']
        if 211 in first_code:
            df = df[df.f211==1]
            first_code.remove(211)
        if 985 in first_code:
            df = df[df.f985==1]
            first_code.remove(985)
        if len(first_code)>0:
            df = df[df.firstrate.isin(first_code)]
    if cfg['mode'] in ['sp', 'group']:
        # sp_code
        if ('major_code_2' in select_list.keys()) and (len(select_list['major_code_2']) > 0):
            df = df[df.major_code_2.isin(select_list['major_code_2'])]
        # demand
        if ('demand' in select_list.keys()) and (len(select_list['demand']) > 0):
            df = df[demand_jg(df, select_list['demand'])]

    # college_id + school_code + sg_name
    df['cl_sg'] = df['college_id'].astype('str')+'_'+df['school_code']+'_'+df['sg_name']

    # clear-1
    df = df[pcls]

    # prob
    df = probability(df, province_id, wenli, score, rank, cfg['cengci'])

    # rename
    df = df.rename({'probability': 'prob', 'college_id': 'cid', 'predict_rank': 'r', 'college_province_id':'pid'}, axis=1)

    # clear-2
    if college_province:
        df = df[['id', 'cid', 'prob', 'cl_sg', 'r', 'pid']]
    else:
        df = df[['id', 'cid', 'prob', 'cl_sg', 'r']]

    # detail
    if detail:
        df = get_data_by_id(df, cfg['mode'], detail_group)
    return df


# 预测概率
# def predict_sg_prob(cfg, df, wenli, score, rank, school_info, detail):
#     province_id = cfg['province_id']
#     # wenli
#     df = df[df.wenli==wenli]
#     # school
#     df = df[df.college_id==school_info['college_id']]
#     df = df[df.school_code==school_info['school_code']]
#     df = df[df.sg_name == school_info['sg_name']]
#     # detail-1
#     if not detail:
#         df = df[keys_sp_plan + prob_cols]
#     # prob
#     df = probability(df, province_id, wenli, score, rank)
#     # detail
#     if not detail:
#         df = df[ sgspkeys()]
#     return df


# 预测院校概率
def predict_college_prob(cfg, df, wenli, score, rank, college_id):
    province_id = cfg['province_id']
    # wenli
    df = df[df.wenli == wenli]
    # college
    df = df[df.college_id==college_id]
    if len(df)>0:
        # prob
        df = probability(df, province_id, wenli, score, rank, cfg['cengci'])
        prob = max(df['probability'])
        if pd.isnull(prob):
            return int(cfg['goal_years']), -1, '-'
        else:
            return int(cfg['goal_years']), prob, get_school_type(prob)
    else:
        return int(cfg['goal_years']), -1, '-'


# 根据概率划分冲稳保
def get_school_type(prob):
    if prob<0:
        return '-'
    if prob>=split_wb:
        return 'bao'
    if prob>=split_cw:
        return 'wen'
    if prob>=split_c:
        return 'chong'
    return 'bo'

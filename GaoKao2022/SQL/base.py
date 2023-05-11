# -*- coding: utf-8 -*-
import pandas as pd
from .setting import *
from mysql.connector import connect


where_base = """category in ("普通类","特殊类") 
                AND gk_period=1 
                AND batch_text not like "%%汉语言%%" AND batch_text not like "%%重点%%" 
                AND batch_text not like "%%蒙授%%" AND batch_text not like "%%藏文%%" 
                AND batch_text not like "%%彝文%%" AND batch_text not like "%%提前%%" 
                AND batch_text not like "%%专项%%" AND batch_text not like "%%预科%%"
                AND batch_text not like "%%特殊%%" AND batch_text not like "%%优投%%"
                AND batch_text not like "%%补%%" AND batch_text not like "%%单招%%" """

where_base_with_stat = where_base + "AND stat=1 "
where_putong = """ AND category="普通类" """


select_type = {
    'college_id': 'int',
    'province_id': 'int',
    'schoolname': 'strs',
    'years': 'int',
    'wenli': 'int',
    'batch_text': 'strs',
    'plan_people': 'int',
    'school_code': 'strs',
    'remark': 'str',
    'enroll_num': 'int',
    'batch_plan': 'strs',
    'batch_fsx': 'strs',

    'predict_minscore': 'float',
    'predict_minscore_std': 'float',
    'predict_rank': 'float',
    'predict_rank_std': 'float',
    'predict_rank_p': 'float',
    'predict_rank_p_std': 'float',

    'minscore': 'int',
    'minscore_rank': 'int',
    'batch_score': 'int',
    'batch_rank': 'int',

    'sp_plan_people': 'int',
    'sp_code': 'str',
    'sp_name': 'str',
    'tuition':  'strs',
    'semester': 'int',
    'demand': 'strs',

    'sg_name': 'strs',
    'sg_remark': 'str',

    'schoolnature': 'int',
    'nature_text': 'strs',
    'f211': 'int',
    'f985': 'int',
    'firstrate': 'int',
    'college_province_id': 'int',
    'college_province': 'strs',
    'city_id': 'int',
    'city': 'strs',
    'typecode': 'int',

    'major_code': 'strs',
    'major_code_1': 'strs',
    'major_code_2': 'strs',


}
# 表中所有的列，其中old的会添加后缀形如_years_wen/li
cols_school = ['province_id', 'college_id', 'schoolname', 'years', 'wenli', 'batch_text', 'batch_plan', 'batch_fsx',
               'plan_people', 'school_code',
               'remark', 'sg_name', 'demand', 'batch_score', 'batch_rank',
               'predict_minscore', 'predict_minscore_std', 'predict_rank',
               'predict_rank_std', 'predict_rank_p', 'predict_rank_p_std',
               'schoolnature', 'nature_text', 'f211', 'f985', 'firstrate', 'college_province_id',
               'college_province', 'city_id', 'city', 'typecode'
               ]
cols_school_old = ['enroll_num', 'minscore', 'minscore_rank', 'batch_score', 'batch_rank']

cols_sp = ['province_id', 'years', 'wenli', 'college_id', 'school_code', 'schoolname', 'sp_code', 'sp_name',
           'major_code', 'major_code_1', 'major_code_2',
           'batch_text', 'batch_plan', 'batch_fsx',
           'sp_plan_people',  'remark', 'tuition', 'semester',  'demand', 'sg_name', 'batch_score',
           'batch_rank',
           'predict_minscore', 'predict_minscore_std', 'predict_rank',
           'predict_rank_std', 'predict_rank_p', 'predict_rank_p_std',
           'schoolnature', 'nature_text', 'f211', 'f985', 'firstrate', 'college_province_id',
           'college_province','city_id', 'city', 'typecode'
           ]
cols_sp_old = ['enroll_num', 'minscore', 'minscore_rank', 'batch_score', 'batch_rank']
# 常驻内存中的df中不需要的列
cols_notdel = ['id',  'wenli', 'batch_score', 'batch_rank', 'predict_minscore', 'predict_minscore_std', 'predict_rank',
               'predict_rank_std', 'predict_rank_p', 'predict_rank_p_std',
               'schoolnature', 'nature_text', 'f211', 'f985', 'firstrate', 'college_province_id',
               'college_province','city_id', 'city', 'typecode', 'major_code', 'major_code_2',
               'demand_1', 'demand_2', 'demand_3', 'demand_concat', 'college_id', 'school_code', 'sg_name',
               'schoolname', 'sp_name']
# 取表列及匹配、group规则
# 院校计划表中取得列
select_plan_school = ['province_id', 'college_id', 'schoolname', 'years', 'wenli', 'batch_text', 'plan_people', 'school_code', 'remark']
# 院校录取表中取得列
select_data_school = ['college_id',  'wenli', 'enroll_num', 'minscore', 'minscore_rank', 'remark']
# 院校录取表去重关键词、计划和录取连表关键词
keys_school = ['college_id', 'wenli', 'remark']
# 院校计划去重关键词
keys_school_plan = ['college_id', 'wenli', 'remark', 'school_code']

# 专业计划表所取列
select_plan_sp = ['province_id', 'years', 'wenli', 'college_id', 'school_code', 'schoolname', 'sp_code', 'sp_name',
                  'sp_remark', 'batch_text', 'sp_plan_people',  'remark', 'tuition', 'semester',  'demand', 'sg_name']
# 专业招生所取列
select_data_sp = ['wenli', 'college_id',  'sp_name', 'enroll_num',  'minscore', 'minscore_rank', 'remark', 'sg_name']
# 招生去重关键词、计划和录取连表关键词
keys_sp = ['college_id', 'wenli', 'sp_name', 'remark', 'sg_name']
# 招生计划去重关键词
keys_sp_plan = ['college_id', 'wenli', 'sp_name', 'remark', 'school_code', 'sp_code', 'sg_name']

# 专业->专业组
# 计划聚类关键值
group_plan_keep = ['province_id', 'college_id', 'schoolname', 'years', 'wenli', 'batch_text',
                   'school_code', 'sg_name', 'demand']
# 计划聚合方式为sum 顺便重命名
group_plan_sum = {'sp_plan_people': 'plan_people'}
# 录取聚合方式为max
group_data_max = ['minscore_rank']
# 录取聚合方式为min
group_data_min = ['minscore']
# 录取聚合方式为sum
group_data_sum = ['enroll_num']
# 录取聚类关键值
group_data_keep = ['batch_score', 'batch_rank']
# 聚类关键值
group_sg = ['college_id', 'wenli', 'school_code', 'sg_name']

# 预测概率所需
prob_cols = [ 'id', 'college_id', 'wenli', 'batch_score', 'batch_rank', 'predict_minscore', 'predict_minscore_std', 'predict_rank',
              'predict_rank_std', 'predict_rank_p', 'predict_rank_p_std', "cl_sg", 'college_province_id']

# 返回字段精简化
result_rename = {
    "college_id": 'ci',
    "sp_name": 'sp',
    "sp_code": 'spc',
    "sg_name": 'sg',
    "remark": 'rm',
    "school_code": 'sc',
    "probability": 'prob',
}


# 获取那几张表是否有stat字段
def get_stat():
    df = pd.read_sql('select * from %s limit 1'%TablePlanSchool, connect(**SQLPlanSchool))
    StatPlanSchool = 'stat' in df.columns

    df = pd.read_sql('select * from %s limit 1'%TableDataSchool, connect(**SQLDataSchool))
    StatDataSchool = 'stat' in df.columns

    df = pd.read_sql('select * from %s limit 1'%TablePlanSp, connect(**SQLPlanSp))
    StatPlanSp = 'stat' in df.columns

    df = pd.read_sql('select * from %s limit 1'%TableDataSp, connect(**SQLDataSp))
    StatDataSp = 'stat' in df.columns

    df = pd.read_sql('select * from %s limit 1'%TableFsx, connect(**SQLFsx))
    StatFsx = 'stat' in df.columns

    df = pd.read_sql('select * from %s limit 1'%TableFsx, connect(**SQLFsd))
    StatFsd = 'stat' in df.columns

    return StatPlanSchool, StatDataSchool, StatPlanSp, StatDataSp, StatFsx, StatFsd


# 检测各个表里是否有stat字段来确定使用哪个basewhere
StatPlanSchool, StatDataSchool, StatPlanSp, StatDataSp, StatFsx, StatFsd = get_stat()


# 根据模式和是否计划获取对应select的字典
# return: 选择目标列， 连表关键词， 计划去重关键词
def select_select(mode, goal):
    if mode == 'school':
        if goal:
            return select_plan_school.copy(), keys_school.copy(), keys_school_plan.copy()
        else:
            return select_data_school.copy(), keys_school.copy(), keys_school_plan.copy()
    if mode in ['sp', 'group']:
        if goal:
            return select_plan_sp.copy(), keys_sp.copy(), keys_sp_plan.copy()
        else:
            return select_data_sp.copy(), keys_sp.copy(), keys_sp_plan.copy()


# 根据模式和是否计划获取对应database和table和basewhere
def select_db_table(mode, goal=True, province_id=0, for_excel=False):
    if mode=='school':
        if goal:
            db = connect(**SQLPlanSchool)
            table = TablePlanSchool
            stat = StatPlanSchool
        else:
            db = connect(**SQLDataSchool)
            table = TableDataSchool
            stat = StatDataSchool
    elif mode in ['group', 'sp']:
        if goal:
            db = connect(**SQLPlanSp)
            table = TablePlanSp
            stat = StatPlanSp
        else:
            db = connect(**SQLDataSp)
            table = TableDataSp
            stat = StatDataSp
    elif mode=='fsx':
        db = connect(**SQLFsx)
        table = TableFsx
        stat = StatFsx
    elif mode=='fsd':
        db = connect(**SQLFsd)
        table = TableFsd
        stat = StatFsd
    if stat:
        wheretxt = where_base_with_stat
    else:
        wheretxt = where_base

    if mode in ['fsx', 'fsd']:
        wheretxt = wheretxt + where_putong
    else:
        if province_id!=19:
            wheretxt = wheretxt + where_putong
        elif province_id==19 and mode=='school':
            wheretxt = wheretxt + where_putong
    if for_excel:
        wheretxt = wheretxt + where_putong
    return db, table, wheretxt

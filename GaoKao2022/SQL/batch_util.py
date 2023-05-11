# -*- coding: utf-8 -*-
from .base import select_db_table
from .rule_util import config
import pandas as pd


# 将批次转化为标准的批次名字
def batch_text2batch(batch_text, log, province_id):
    # 特殊情况
    if (province_id == 11):
        base = "平行录取"
        return base
    elif (province_id==15):
        if ("一段" in batch_text) or ("一次" in batch_text) or ("本" in batch_text):
            base = "一段"
        elif ("二段" in batch_text) or ("二次" in batch_text) or ("三次" in batch_text) or ("专" in batch_text) or ("高职" in batch_text):
            base = "二段"
        else:
            log.error("未知批次：%s"%batch_text)
            base = ""
        return base
    # 正常省份
    base, extra = "", ""
    if "本" in batch_text:
        if "一" in batch_text:
            base = "本科一批"
        elif "二" in batch_text:
            base = "本科二批"
        elif "三" in batch_text:
            base = "本科三批"
        else:
            base = "本科批"
    elif ("专科" in batch_text) or ("高职" in batch_text):
        base = "专科批"
    # 后缀
    if 'A1' in batch_text:
        extra = 'A1'
    elif 'A' in batch_text:
        extra = ''
    elif 'B' in batch_text:
        extra = 'B'
    elif 'C' in batch_text:
        extra = 'C'
    result = base+extra
    if result == '':
        log.info("批次格式化异常:%s"%batch_text)
    return result


# 获取给定条件的所有批次
def get_all_batch(years, province_id, mode, goal):
    db, table, wheretxt = select_db_table(mode, goal, province_id)
    sql_text = "SELECT batch_text FROM %s WHERE years=%s AND province_id=%s AND %s GROUP BY batch_text" \
               % (table, years, province_id, wheretxt)
    if mode=='fsx':
        sql_text = "SELECT batch_text FROM %s WHERE years=%s AND province_id=%s AND %s " \
                   "GROUP BY batch_text" \
                   % (table, years, province_id, wheretxt)
        # 浙江要用倒序，取分数最高的作为批次线，其他省份都是取最低的作为批次线
        if province_id==11:
            sql_text += " ORDER BY score DESC"
    batch = pd.read_sql(sql_text, db)
    db.close()
    return list(batch.batch_text)


# 选择招生计划中相匹配的批次
def batch_mark_goal(batch, goals, batch_all, goal_org, log):
    gs = goals.copy()
    gs.sort()
    batch_all.sort()
    result = []
    for i in range(len(goals)):
        if batch==goals[i]:
            result.append(goal_org[i])
    if len(result)>0:
        log.info("[招生计划批次] %s -> %s" % (goal_org, result))
    else:
        log.warning("[招生计划批次] %s -> None"%goal_org)
    return result


# 选择招生计划年份批次线中相匹配的批次，只选择最符合的一条
def batch_mark_fsx_goal(batch, goals, batch_all, goal_org, log):
    dt = goals.copy()
    dt.sort()
    batch_all.sort()
    result = ""
    # 完美情况
    if dt == batch_all:
        for i in range(len(goals)):
            if batch == goals[i]:
                result = goal_org[i]
    else:
        result_indexs = batch_data_select(batch, batch_all, goals, hard=False)
        if len(result_indexs)>0:
            result = goal_org[result_indexs[0]]
    if result:
        log.info("[批次线批次] %s -> %s" % (goal_org, result))
    else:
        log.warning("[批次线批次] %s -> None" % (goal_org))
    return result


# key in any of the list
def inany(key, blist):
    for b in blist:
        if key in b:
            return True
    return False


# 获取所有候选对应 不改变次序
def batch_data_select(batch, batch_all, datas, hard=True):
    ksall = ['本科', '专科', '段', 'A1', 'B', 'C'] if hard else ['本科', '专科', '段']
    bnum = []
    if '一' in batch:
        bnum.append('一')
    elif '二' in batch:
        if inany('三', batch_all):
            bnum.append('二')
        else:
            bnum.append('二')
            bnum.append('三')
    elif '三' in batch:
        bnum.append('三')

    result_indexs = []
    for i in range(len(datas)):
        sign = True
        # keys全部满足
        for k in ksall:
            if ((k in batch) and (k not in datas[i])) or ((k not in batch) and (k in datas[i])):
                sign = False
                break
        if sign:
            # bnum非空时任一满足
            if len(bnum) == 0:
                result_indexs.append(i)
            else:
                for b in bnum:
                    if b in datas[i]:
                        result_indexs.append(i)
                        break
    return result_indexs


# 选择录取年份批次线中相匹配的批次，只选择最低的一条
def batch_mark_fsx_data(batch, datas, batch_all, datas_org, log):
    dt = datas.copy()
    dt.sort()
    batch_all.sort()
    result = False
    # 完美情况
    if dt == batch_all:
        for i in range(len(datas)):
            if batch == datas[i]:
                result = datas_org[i]
    else:
        result_indexs = batch_data_select(batch, batch_all, datas, hard=False)
        if len(result_indexs)>0:
            result = datas_org[result_indexs[0]]
    if result:
        log.info("[分数线批次] %s -> %s" % (datas_org, result))
    else:
        log.warning("[分数线批次] %s -> None" % (datas_org))
    return result


# 选择往年录取数据中相匹配的批次
def batch_mark_data(batch, datas, batch_all, datas_org, log):
    dt = datas.copy()
    dt.sort()
    batch_all.sort()
    result = []
    # 完美情况
    if dt == batch_all:
        for i in range(len(datas)):
            if batch == datas[i]:
                result.append(datas_org[i])
    else:
        result_indexs = batch_data_select(batch, batch_all, datas)
        for i in result_indexs:
            result.append(datas_org[i])
    if len(result) > 0:
        log.info("[录取批次] %s -> %s" % (datas_org, result))
    else:
        log.warning("[录取批次] %s -> None" % (datas_org))
    return result


# batch list norm
def batch_list_norm(batch_list, log, province_id):
    batchroom = []
    batchorg = []
    for batch in batch_list:
        batchresult = batch_text2batch(batch, log, province_id)
        if batchresult == '':
            pass
        else:
            batchroom.append(batchresult)
            batchorg.append(batch)
    return batchroom, batchorg


# 从所有批次中选择最匹配的批次
def select_best_batch(batch, batch_texts, type, batch_all, log, province_id=0):
    """
    :param batch: 当前标准名字的批次
    :param batch_texts: 所有当前批次
    :param type: 类型——goal/data/fsx_goal/fsx_data
    :param batch_all: 所有标准名字的批次
    :return:
    """
    assert type in ['goal', 'fsx_goal', 'data', 'fsx_data'], '未知type'
    batch_norms, batch_texts = batch_list_norm(batch_texts, log, province_id)
    if '' in batch_norms:
        batch_norms.remove('')
    # batch, batch_all 标准批次和所有的标准批次
    # batch_norm, batch_texts 当前批次的标准名字列表 当前批次的原列表
    if type == 'goal':
        return batch_mark_goal(batch, batch_norms, batch_all, batch_texts, log)
    if type == 'fsx_goal':
        return batch_mark_fsx_goal(batch, batch_norms, batch_all, batch_texts, log)
    if type == 'data':
        return batch_mark_data(batch, batch_norms, batch_all, batch_texts, log)
    if type == 'fsx_data':
        return batch_mark_fsx_data(batch, batch_norms, batch_all, batch_texts, log)
    return


# 获取批次对应的[招生计划][录取数据][分数线]中的实际批次名字
def get_batch_true(province_id, goal_years, batch_result, log, batch_text_all):
    mode, years = batch_result['mode'], batch_result['years']
    batch_text = batch_result['batch_text']
    # 获取今年的招生计划的batch list
    log.info("★[招生计划][%s]★" % goal_years)
    goal_batch_list = get_all_batch(goal_years, province_id, mode, True)
    goal_batch = select_best_batch(batch_text, goal_batch_list, "goal", batch_text_all, log, province_id)
    if len(goal_batch)==0:
        log.warning("☹%s年：未找到招生计划"%goal_years)
        if abs(years-goal_years)>2:
            log.error("☹☹未找到近两年招生计划")
            return False
        return get_batch_true(province_id, goal_years-1, batch_result, log, batch_text_all)
    batch_result['goal_years'] = goal_years
    batch_result['goal_batch'] = goal_batch
    # 获取今年批次线里面对应的batch list
    sf_batch_list = get_all_batch(goal_years, province_id, "fsx", True)
    sf_batch = select_best_batch(batch_text, sf_batch_list, "fsx_goal", batch_text_all, log, province_id)
    if sf_batch:
        batch_result['goal_sf_batch'] = sf_batch
    else:
        log.warning("☹%s年：未找到省控线" % goal_years)
        goal_years = goal_years - 1
        sf_batch_list = get_all_batch(goal_years, province_id, "fsx", True)
        sf_batch = select_best_batch(batch_text, sf_batch_list, "fsx_goal", batch_text_all, log, province_id)
        if sf_batch:
            batch_result['goal_sf_batch'] = sf_batch
        else:
            batch_result['goal_sf_batch'] = ''
            log.warning("☹%s年：未找到省控线" % goal_years)
    # 获取往年的batch list
    for i in range(config['year_old']):
        data_year = years - i - 1
        log.info("★[录取数据][%s年]★"%data_year)
        # 分数表中
        data_batch_list = get_all_batch(data_year, province_id, mode, False)
        data_batch = select_best_batch(batch_text, data_batch_list, "data", batch_text_all, log, province_id)
        batch_result['data_batch_%s'%data_year] = data_batch
        # 批次线中
        sf_batch_list = get_all_batch(data_year, province_id, "fsx", False)
        sf_batch = select_best_batch(batch_text, sf_batch_list, "fsx_data", batch_text_all, log, province_id)
        batch_result['data_sf_batch_%s' % data_year] = sf_batch
    return batch_result

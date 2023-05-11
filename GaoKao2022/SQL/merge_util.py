# -*- coding: utf-8 -*-
from .base import *
from .rule_util import config, varchar_length
from .sf_util import get_sf, get_fsd, get_score_rank
from .spname_util import clear_spname, get_sp_code, spname_cols, clear_remark
import pandas as pd


# group for merge
def group(df, keys, log):
    ori_len = len(df)
    df.drop_duplicates(keys, keep='first', inplace=True)
    now_len = len(df)
    log.info('去重去除%s行' % (ori_len-now_len))
    return df


# 文理转换
def transform_trans(df):
    df.wenli = df.wenli + 20
    return df


# 文理合并
def transform_cos(df, keys):
    df_wen = df[df.wenli==1]
    df_li = df[df.wenli==2]
    df_uk = df[df.wenli==0]
    df_wen.wenli = 0
    df_li.wenli = 0
    for col in df.columns:
        if col not in keys:
            df_wen = df_wen.rename({col:col+'_wen'}, axis=1)
            df_li = df_li.rename({col: col + '_li'}, axis=1)
    # df = pd.merge(df_wen, df_li, on=keys, how='outer')
    # return df
    if len(df_uk)==0:
        return [df_wen, df_li]
    else:
        return [df_uk, df_wen, df_li]


# 历史数据格式转换
def transform(df, year, cols, keys, mode='school', ts=None):
    if ts == 'trans':
        df = transform_trans(df)
    if mode != 'school':
        keys = keys + spname_cols
    for col in df.columns:
        if col not in keys:
            df = df.rename({col: col+'_%s'%year}, axis=1)
    if ts == 'cos':
        df = transform_cos(df, keys)
        return df
    else:
        return [df]


# 获取招生计划
def get_goal(cfg, log):
    db, table, wheretxt = select_db_table(cfg['mode'], goal=True, province_id=cfg['province_id'])
    cols, _, keys_plan = select_select(cfg['mode'], goal=True)

    if (len(cfg['goal_wenli'])==0) or (len(cfg['goal_batch'])==0):
        log.error("获取招生计划失败，因为wenli:%s错误或batch:%s错误"%(cfg['goal_wenli'], cfg['goal_batch']))
        return []

    sql_text = 'SELECT {select} ' \
               'FROM {table} ' \
               'WHERE years={year} ' \
               'AND province_id={province} ' \
               'AND wenli in {wenli} ' \
               'AND batch_text in {batchs} ' \
               'AND {where}'.format(select=', '.join(cols),
                                    table=table,
                                    year=cfg['goal_years'],
                                    province=cfg['province_id'],
                                    wenli=str(tuple(cfg['goal_wenli'])).replace(',)', ')'),
                                    batchs=str(tuple(cfg['goal_batch'])).replace(',)', ')'),
                                    where=wheretxt)
    df_goal = pd.read_sql(sql_text, db)
    db.close()
    log.info("★[招生计划:%s]★ %s" % (cfg['goal_years'], len(df_goal)))

    df_goal['batch_plan'] = df_goal['batch_text']
    df_goal['batch_fsx'] = cfg['goal_sf_batch'] if cfg['goal_sf_batch'] else ''
    df_goal['batch_text'] = cfg['batch_text'] if cfg['batch_text'] else ''

    if cfg['mode'] in ['sp', 'group']:
        df_goal['remark'] = df_goal.apply(lambda x: str(x['sp_remark']) + str(x['remark']), axis=1)
        df_goal = df_goal.drop('sp_remark', axis=1, inplace=False)

        df_goal[spname_cols] = df_goal[['sp_name', 'remark', 'semester']]\
            .apply(lambda x: clear_spname(x), axis=1, result_type='expand') if len(df_goal)>0 else ''
        # df_goal[spname_cols] = pd.DataFrame(df_goal[['sp_name', 'remark', 'semester']].apply(lambda x: clear_spname(x), axis=1)
        #                                     .tolist()) if len(df_goal)>0 else ''
        df_goal = get_sp_code(df_goal, cfg['cengci'])
    else:
        df_goal['remark'] = df_goal['remark'].apply(lambda x: clear_remark(x)) if len(df_goal)>0 else ''

    df_goal_sf = get_sf(cfg, cfg['goal_years'], cfg['goal_sf_batch'], log)
    df_goal = pd.merge(df_goal, df_goal_sf, on=['wenli'], how='left')

    df_goal = group(df_goal, keys_plan, log)
    return df_goal


# 尝试通过一份一段段获取排名
def get_history_rank(df, cfg, year, log):
    fsd = get_fsd(cfg['province_id'], year, cfg['gaozhi'])
    df['minscore_rank'] = df.apply(lambda x: get_score_rank(fsd, x.minscore, x.wenli) \
        if (not x.minscore_rank>0) and x.minscore>0 else x.minscore_rank,
                                   axis=1)
    return df


# 获取历史数据
def get_history(cfg, log):
    if ('for_excel' in cfg.keys()) and cfg['for_excel']:
        return get_history_for_excel(cfg, log)
    db, table, wheretxt = select_db_table(cfg['mode'], goal=False, province_id=cfg['province_id'])
    cols, keys, _ = select_select(cfg['mode'], goal=False)
    data = []
    for i in range(config['year_old']):
        year = cfg['years'] - 1 - i
        # 有可能没选到任何往事
        if (len(cfg['data_batch_%s'%year])==0) or (len(cfg['data_wenli_%s'%year])==0):
            log.warning("无法获取%s年录取数据"%year)
            continue
        sql_text = 'SELECT {select} ' \
                   'FROM {table} ' \
                   'WHERE years={year} ' \
                   'AND province_id={province} ' \
                   'AND wenli in {wenli} ' \
                   'AND batch_text in {batchs} ' \
                   'AND {where}'.format(select=', '.join(cols),
                                        table=table,
                                        year=year,
                                        province=cfg['province_id'],
                                        wenli=str(tuple(cfg['data_wenli_%s'%year])).replace(',)', ')'),
                                        batchs=str(tuple(cfg['data_batch_%s'%year])).replace(',)', ')'),
                                        where=wheretxt)
        df = pd.read_sql(sql_text, db)
        log.info("★[录取分数:%s]★ %s" % (year, len(df)))
        # 保留最小排名
        df.sort_values(by=['minscore', 'minscore_rank'], ascending=[False, True], axis=0, inplace=True)
        df = group(df, keys, log)
        # 填补排名
        df = get_history_rank(df, cfg, year, log)
        # spname
        if cfg['mode'] in ['sp', 'group']:
            df[spname_cols] = df[['sp_name', 'remark']].apply(lambda x: clear_spname(x), axis=1, result_type='expand')\
                if len(df)>0 else ''
        # remark
        else:
            df['remark'] = df['remark'].apply(lambda x: clear_remark(x)) if len(df)>0 else ''
            df = group(df, keys, log)
        # 省控线
        df_sf = get_sf(cfg, year, cfg['data_sf_batch_%s'%year], log)
        df = pd.merge(df, df_sf, on=['wenli'], how='left')
        # trans
        df = transform(df, year, cols, keys, mode=cfg['mode'], ts=cfg['data_ts_wenli_%s' % year])
        # 更名
        data.extend(df)
    db.close()
    return data


# 获取历史数据_为了获取Excel表
def get_history_for_excel(cfg, log):
    # 录取数据
    db, table, wheretxt = select_db_table(cfg['mode'], goal=False, province_id=cfg['province_id'], for_excel=True)
    cols, keys, _ = select_select(cfg['mode'], goal=False)
    # 专业组使用招生计划校验
    if cfg['org_mode']=='group':
        cols.append('sg_name')
        dbp, tablep, wheretxtp = select_db_table('sp', goal=True, province_id=cfg['province_id'], for_excel=True)

    data = []
    for i in range(config['year_old']):
        year = cfg['years'] - 1 - i
        # 有可能没选到任何往事
        if (len(cfg['data_batch_%s'%year])==0) or (len(cfg['data_wenli_%s'%year])==0):
            log.warning("无法获取%s年录取数据"%year)
            continue
        sql_text = 'SELECT {select} ' \
                   'FROM {table} ' \
                   'WHERE years={year} ' \
                   'AND province_id={province} ' \
                   'AND wenli in {wenli} ' \
                   'AND batch_text in {batchs} ' \
                   'AND {where}'.format(select=', '.join(cols),
                                        table=table,
                                        year=year,
                                        province=cfg['province_id'],
                                        wenli=str(tuple(cfg['data_wenli_%s'%year])).replace(',)', ')'),
                                        batchs=str(tuple(cfg['data_batch_%s'%year])).replace(',)', ')'),
                                        where=wheretxt)
        df = pd.read_sql(sql_text, db)
        if (21 in cfg['data_wenli_%s'%year]) and (cfg['org_mode']=='group'):
            # batch不一定对得上
            sql_plan = 'SELECT wenli, college_id, sg_name, MAX(sp_plan_people) plan_people ' \
                       'FROM {table} ' \
                       'WHERE years={year} ' \
                       'AND province_id={province} ' \
                       'AND wenli in {wenli} ' \
                       'AND batch_text in {batchs} ' \
                       'AND {where} ' \
                       'GROUP BY wenli, college_id, sg_name'\
                .format(table=tablep,
                        year=year,
                        province=cfg['province_id'],
                        wenli=str(tuple(cfg['data_wenli_%s'%year])).replace(',)', ')'),
                        batchs=str(tuple(cfg['data_batch_%s'%year])).replace(',)', ')'),
                                            where=wheretxtp)
            df_p = pd.read_sql(sql_plan, dbp)
            df = pd.merge(df, df_p, on=['wenli', 'college_id', 'sg_name'], how='left')
            log.info("★[录取分数去特殊类:%s]★ %s" % (year, sum(pd.isnull(df.plan_people))))
            df = df[~pd.isnull(df.plan_people)]
        log.info("★[录取分数:%s]★ %s" % (year, len(df)))
        # 保留最大排名
        if cfg['org_mode']=='group':
            df.sort_values(by=['minscore', 'minscore_rank'], ascending=[True, False], axis=0, inplace=True)
        else:
            df.sort_values(by=['minscore', 'minscore_rank'], ascending=[False, True], axis=0, inplace=True)

        df = group(df, keys, log)
        # 填补排名
        df = get_history_rank(df, cfg, year, log)
        # spname
        if cfg['mode'] in ['sp', 'group']:
            df[spname_cols] = df[['sp_name', 'remark']].apply(lambda x: clear_spname(x), axis=1, result_type='expand') \
                if len(df) > 0 else ''
        # remark
        else:
            df['remark'] = df['remark'].apply(lambda x: clear_remark(x)) if len(df)>0 else ''
            df = group(df, keys, log)
        # 省控线
        df_sf = get_sf(cfg, year, cfg['data_sf_batch_%s'%year], log)
        df = pd.merge(df, df_sf, on=['wenli'], how='left')
        # trans
        df = transform(df, year, cols, keys, mode=cfg['mode'], ts=cfg['data_ts_wenli_%s' % year])
        # 更名
        data.extend(df)
    db.close()
    return data




def myfirst(df):
    return df.iloc[0]


def myalllist(df):
    return list(set(df))


def data_isnull(df, year, cfg):
    if cfg['data_ts_wenli_%s'%year] == 'cos':
        if 'minscore_%s_wen'%year in df.columns:
            return pd.isnull(df['minscore_%s_wen'%year])
        if 'minscore_%s_wen'%year in df.columns:
            return pd.isnull(df['minscore_%s_wen'%year])
    return pd.isnull(df['minscore_%s'%year])


# 获取数据实装
def merge_data(cfg, df, data, log):
    _, keys, _ = select_select(cfg['mode'], goal=False)
    if cfg['mode'] == 'school':
        log.info('★院校招生模式★'%keys)
        for d in data:
            df = pd.merge(df, d, on=keys, how='left')
            # log
            for c in d.columns:
                if 'minscore' in c and 'rank' not in c:
                    if 'wen' not in c and 'li' not in c:
                        year = int(c[-4:])
                    else:
                        year = int(c[9:13])
            log.info('%s匹配数量:%s'%(year, len(df)-sum(data_isnull(df, year, cfg))))

    elif cfg['mode'] in ['sp', 'group']:
        log.info('★专业(组)招生模式★')
        keybase = ['college_id', 'wenli']

        key_perfect = spname_cols
        key_perfect_sg = key_perfect.copy()
        key_perfect_sg.append('sg_name')

        key_good_sg = ['spname_base', 'spname_name', 'spname_sem', 'sg_name', 'spname_extra']
        key_good = ['spname_base', 'spname_name', 'spname_sem', 'spname_extra']

        key_ok_sg = ['spname_base', 'spname_name',  'spname_sem','sg_name']
        key_ok = ['spname_base', 'spname_name',  'spname_sem']

        key_can_sg = ['spname_base', 'spname_name', 'sg_name']
        key_can = ['spname_base', 'spname_name']

        log.debug('[招生计划]%s条' % len(df))
        for i in range(len(data)):
            d = data[i]
            for c in d.columns:
                if 'minscore' in c and 'rank' not in c:
                    if 'wen' not in c and 'li' not in c:
                        year = int(c[-4:])
                    else:
                        year = int(c[9:13])
            log.debug('[%s]录取数据%s条' % (year, len(d)))
            df_done = []
            cols_plan = df.columns
            # 专业组省份且之前也是专业组省份
            if (cfg['data_ts_wenli_%s' % year]=='keep') and (cfg['mode']=='group'):
                onlist = [keys + key_perfect, keybase + key_perfect_sg, keybase + key_good_sg, keybase + key_ok_sg,
                          keybase + key_can_sg, keybase + key_can]
            else:
                onlist = [keys + key_perfect, keybase + key_perfect, keybase + key_good, keybase + key_ok,
                          keybase + key_can]
            for k in onlist:
                d = d.drop_duplicates(k, keep='first', inplace=False)
                for delcol in keys+key_perfect_sg:
                    if (delcol not in k) and (delcol in d.columns):
                        d = d.drop(delcol, axis=1, inplace=False)
                df = pd.merge(df, d, on=k, how='left')
                df_done.append(df[~data_isnull(df, year, cfg)])
                df = df[data_isnull(df, year, cfg)][cols_plan]
            df = pd.merge(df, d, on=k, how='left')
            df_done.append(df)
            log.debug("匹配情况：%s"%([len(dd) for dd in df_done]))
            df = pd.concat(df_done, axis=0)
        for cl in spname_cols:
            df.drop(cl, axis=1, inplace=True)
    return df


# 类型转换清理
def transtype(key, dic, df, dfkey):
    if 'strs' == dic[key]:
        df[dfkey] = df[dfkey].apply(lambda x: '' if pd.isnull(x) else str(x)[:varchar_length['strs']])
    elif 'str' == dic[key]:
        df[dfkey] = df[dfkey].apply(lambda x: '' if pd.isnull(x) else str(x)[:varchar_length['str']])
    elif dic[key] == 'int':
        df[dfkey] = df[dfkey].apply(lambda x: -1 if pd.isnull(x) else int(x))
    elif dic[key] == 'float':
        df[dfkey] = df[dfkey].apply(lambda x: -1.0 if pd.isnull(x) else float(x))
    return df


# 数据格式化
def clear_data(cfg, df, log):
    cols = select_type.copy()
    for col in df.columns:
        if col in cols.keys():
            df = transtype(col, cols, df, col)
        else:
            for chead in cols:
                if chead == col[:len(chead)]:
                    df = transtype(chead, cols, df, col)
                    break
    return df


# sp->sg
def group_data(cfg, df, log):
    if cfg['mode']!='group':
        log.info("并非专业组类型，无需操作")
        return df
    result = dict()
    for c in df.columns:
        if c in group_plan_keep:
            result[c] = 'first'
        if c in group_plan_sum.keys():
            result[c] = 'sum'
        else:
            for gc in group_data_max:
                if gc == c[:len(gc)]:
                    result[c] = 'first'
            if c in result.keys():
                continue
            for gc in group_data_min:
                if gc == c[:len(gc)]:
                    result[c] = 'first'
            if c in result.keys():
                continue
            for gc in group_data_keep:
                if gc == c[:len(gc)]:
                    result[c] = 'first'

    # df.sort_values('minscore_rank_2021', ascending=False, axis=0, inplace=True)

    df = df.groupby(by=group_sg, as_index=False).agg(result)
    df = df.rename(group_plan_sum, axis=1)
    return df

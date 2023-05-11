# -*- coding: utf-8 -*-
from GaoKao2022.Util.logging import logger
from GaoKao2022.SQL import get_rule, get_batch_true, get_wenli_true, get_goal, get_history, merge_data, clear_data
from GaoKao2022.SQL import del_sql_batch, save2mysql, creat_table, data_is_exist, del_sql_not_batch
from GaoKao2022.SQL import config, goal_table_exist, delete_table, clear_demand, merge_college_info
from GaoKao2022.SQL import cols_notdel, myfirst, myalllist, df2excel
from GaoKao2022.Predict2022 import predict_new


# 读取数据库存在内存前所进行的操作
def transform_after_sql(cfg, df):
    if cfg['mode'] in ['group', 'sp']:
        df[['demand_1', 'demand_2', 'demand_3', 'demand_concat']] = df[['demand', 'school_code']].apply(
            lambda x: clear_demand(x['demand']), axis=1, result_type='expand')
    for col in df.columns:
        if col not in cols_notdel:
            df = df.drop([col], axis=1)
    return df


# 每一个批次
def batch_main(province_id, rule, log, batchs):
    if type(rule)!=dict:
        dict_batch = rule.to_dict()
    else:
        dict_batch = rule
    batch_text = rule['batch_text']

    log.info("★★★★★[%s]①获取批次信息★★★★★" % batch_text)
    dict_batch = get_batch_true(province_id, dict_batch['years'], dict_batch, log, batchs)
    if not dict_batch:
        log.info("☹☹☹☹☹[%s]没有招生计划，处理失败☹☹☹☹☹" % batch_text)
        return {}

    log.info("★★★★★[%s]②获取wenli信息★★★★★" % batch_text)
    dict_batch = get_wenli_true(province_id, dict_batch, log)

    log.info("★★★★★[%s]③获取招生计划★★★★★" % batch_text)
    df = get_goal(dict_batch, log)
    if len(df)==0:
        log.info("☹☹☹☹☹[%s]获取计划失败，终止处理☹☹☹☹☹" % batch_text)
        return {}

    log.info("★★★★★[%s]④获取招生记录★★★★★" % batch_text)
    data = get_history(dict_batch, log)
    if len(data)==0:
        log.info("☹☹☹☹☹[%s]获取录取数据失败，终止处理☹☹☹☹☹" % batch_text)
        return {}

    log.info("★★★★★[%s]⑤拼接计划与记录★★★★★" % batch_text)
    df = merge_data(dict_batch, df, data, log)

    log.info("★★★★★[%s]⑥获取院校信息★★★★★" % batch_text)
    df = merge_college_info(dict_batch, df, log)

    log.info("★★★★★[%s]⑦数据格式化处理★★★★★" % batch_text)
    df = clear_data(dict_batch, df, log)

    log.info("★★★★★[%s]⑧预测最新排名★★★★★" % batch_text)
    df = predict_new(df, dict_batch)

    # 如果是生成excel表格，则无需专业，直接返回
    if ('for_excel' in dict_batch.keys()) and dict_batch['for_excel']:
        return {'data': df, 'cfg': dict_batch}

    if dict_batch['mode']=='school':
        log.info("★★★★★[%s]⑨旧高考省份追加处理专业★★★★★" % batch_text)
        cfg_temp = dict_batch.copy()
        cfg_temp['mode'] = 'sp'
        df_sp = get_goal(cfg_temp, log)
        df_sp = clear_data(cfg_temp, df_sp, log)

    if len(df) > 0:
        # df = transform_after_sql(dict_batch, df)
        if dict_batch['mode']=='school':
            return {'data': df, 'cfg': dict_batch, 'data_sp': df_sp}
        else:
            return {'data': df, 'cfg': dict_batch}
    else:
        return {}


# 读取数据库
def get_from_sql(province_id, rule, log):
    log.info("★★★★★从数据库中获取数据★★★★★")
    df = data_is_exist(province_id, rule['batch_text'], rule['mode'])
    if len(df)>0:
        config = rule.copy()
        # 以此判断是否刚存进库里的数据，刚生成的cfg中应该已包含各种字段
        if 'goal_years' in config.keys():
            # 校验是否出错,无错之后可以改成直接返回
            dfcfg = df.groupby(by=['province_id', 'batch_text']).agg({
                'batch_plan': myalllist,
                'batch_fsx': myfirst,
                'province_id': myfirst,
                'years': myfirst,
            })
            if (config['goal_years']==dfcfg.years.iloc[0]) and (config['goal_batch'] == dfcfg.batch_plan.iloc[0]) \
                and (config['goal_sf_batch'] == dfcfg.batch_fsx.iloc[0]):
                pass
            else:
                log.error("读取数据生成config时存在异常！！！")
        else:
            dfcfg = df.groupby(by=['province_id', 'batch_text']).agg({
                'batch_plan': myalllist,
                'batch_fsx': myfirst,
                'province_id': myfirst,
                'years': myfirst,
            })
            # 后面的if是为了兼容之前可能存在的生成表中批次为'False'的情况，理论上现在已经不会出现了
            config['goal_years'] = dfcfg.years.iloc[0] if dfcfg.years.iloc[0]!='False' else ''
            config['goal_batch'] = dfcfg.batch_plan.iloc[0] if dfcfg.batch_plan.iloc[0]!='False' else ''
            config['goal_sf_batch'] = dfcfg.batch_fsx.iloc[0] if dfcfg.batch_fsx.iloc[0]!='False' else ''
        df = transform_after_sql(config, df)
        return {'data': df, 'cfg': config}
    else:
        log.info("☹☹☹☹☹数据为空☹☹☹☹☹")
        return {}


# 写入数据库
def wirte_to_sql(df, cfgorg, mode, log):
    cfg = cfgorg.copy()
    if mode:
        cfg['mode'] = mode
    if save2mysql(df, cfg, log):
        log.info("[MYSQL]保存成功")


# 每一个省份
def province_main(province_id, replace):
    """
    replace: soft:只读库中，try:库中没有则重新生成，hard:强制重新生成
    """
    # 日志
    log = logger(province_id)
    log.info("╞════════════════════════════════%s号省═════════════════════════════════╡" % province_id)
    # 获取批次
    rule, batch = get_rule(province_id)  # batch:str[]
    log.info("[RULE]需要处理批次：%s"%batch)
    log.info("[RULE]replace：%s" % replace)
    # 保存到内存
    result = {}
    # soft
    if replace == 'soft':
        for batch_text in batch:
            log.info("╞══════════════BATCH:%s══════════════╡" % batch_text)
            batch_rule = rule[rule.batch_text == batch_text].iloc[0]
            batch_rule = batch_rule.to_dict()
            dff = get_from_sql(province_id, batch_rule, log)
            if len(dff.keys()) > 0:
                result[batch_text] = dff
        return result, batch
    # hard
    if replace == 'hard':
        # 先处理
        for batch_text in batch:
            log.info("╞══════════════BATCH:%s══════════════╡" % batch_text)
            batch_rule = rule[rule.batch_text == batch_text].iloc[0]
            dff = batch_main(province_id, batch_rule, log, batch)
            if len(dff.keys()) > 0:
                result[batch_text] = dff
        # 所有批次处理完成后再统一保存
        for batch_text in result.keys():
            if result[batch_text]['cfg']['mode'] == 'school':
                wirte_to_sql(result[batch_text]['data_sp'], result[batch_text]['cfg'], 'sp', log)
                wirte_to_sql(result[batch_text]['data'], result[batch_text]['cfg'], None, log)
            else:
                wirte_to_sql(result[batch_text]['data'], result[batch_text]['cfg'], None, log)
        # 删除其他批次
        log.info("[MYSQL]清除可能存在的旧批次数据")
        del_sql_not_batch(province_id, list(result.keys()), log)
        # 最后读表返回
        for batch_text in result.keys():
            log.info("╞══════════════BATCH:%s══════════════╡" % batch_text)
            batch_rule = result[batch_text]['cfg']
            dff = get_from_sql(province_id, batch_rule, log)
            if len(dff.keys()) > 0:
                result[batch_text] = dff
        return result, batch


# 尝试创建目标表格
def try_creat(log):
    try:
        creat_table()
        log.debug("重建school和sp表")
    except:
        log.error("已存在school和sp表格")


# 清空所有表格
def restart_all(log):
    try:
        delete_table()
        return True
    except:
        log.error("删除所有表格失败，可能某些表格不存在")
        return False


def init_data_province(province):
    replace = 'soft'
    result = province_main(province, replace)
    return result


# 数据更新
def updata_data_province(province_id):
    result = province_main(province_id, 'hard')
    return result


# 获取榜单
def get_bangdan(province_id):
    log = logger("rank"+str(province_id))
    log.info("╞════════════════════════════════%s号省排行榜═════════════════════════════════╡" % province_id)
    # 获取批次
    rule, batch = get_rule(province_id)  # batch:str[]
    log.info("[RULE]需要处理批次：%s"%batch)
    result = {}
    for batch_text in batch:
        log.info("╞══════════════BATCH:%s══════════════╡" % batch_text)
        batch_rule = rule[rule.batch_text == batch_text].iloc[0]
        cfg = batch_rule.to_dict()
        cfg['org_mode'] = cfg['mode']
        cfg['mode'] = 'school'
        cfg['for_excel'] = True
        dff = batch_main(province_id, cfg, log, batch)
        if len(dff.keys()) > 0:
            result[batch_text] = dff
    data = df2excel(result)
    return data




if __name__ == '__main__':
    try:
        creat_table()
    except:
        print("已存在表格")

    from GaoKao2022 import predict_prob

    # result = province_main(1, 'try')
    # rb = result['本科批']
    # df = predict_prob(rb['cfg'], rb['data'], 0, 555, 6666, ["物理","化学","生物"], False)
    # dfg = predict_sg_prob(rb['cfg'], rb['data_sg'], 0, 555, 6666, {"college_id":39,"sg_name":"02","school_code":"1025"}, False)
    #
    # result = province_main(3, 'try')
    # rb = result['本科批']
    # df = predict_prob(rb['cfg'], rb['data'], 22, 555, 6666, ["物理","化学","生物"], False)

    result, _ = province_main(1, 'hard')
    rb = result['本科批']
    import time
    a= time.time()
    s = {
            "college_id": -1,
            "city_id": [],
            "major_code_2": [],
            "nature_code": [],
            "first_code": [],
            "type_code": [],
            "demand": [],
            "keyword": "",
    }
    df = predict_prob(rb['cfg'], rb['data'], 22, 666, 66666, s, False)
    print("用时:", time.time()-a)


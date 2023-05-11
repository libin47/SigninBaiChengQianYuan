# -*- coding: utf-8 -*-
from .main import updata_data_province, init_data_province, restart_all, try_creat, get_bangdan
from .SQL.rule_util import config
from .SQL.sql_util import goal_table_exist, delete_rule_table, del_sql_province, set_table_type
from .Predict import predict_prob, predict_college_prob, split_c, split_cw, split_wb
from .Util import id2province
from .Util.logging import logger
from .Rule import try_creat_rule_table
from .SQL.setting import BATCH_LIST, ALL_SIGN, DF_DATA, CONFIG, DF_EXCEL, SUCCESS_SIGN, LOG_DATA
from .SQL.to_excel import download_excel
import redis
import pickle
import traceback
mainlog = logger(0)



# 数据初始化
def init_data_space(log, flush=False):
    try_creat_rule_table(log)
    if not goal_table_exist():
        log.debug("重建school和sp表")
        try_creat(log)
    if flush:
        for r in [BATCH_LIST, ALL_SIGN, DF_DATA, CONFIG, DF_EXCEL, SUCCESS_SIGN, LOG_DATA]:
            r.flushdb()
    # 重启时更新所有状态
    for i in range(31):
        ALL_SIGN.set(str(i)+'_init', 0)
        ALL_SIGN.set(str(i)+'_update', 0)
        ALL_SIGN.set(str(i)+'_excel', 0)
        ALL_SIGN.set(str(i)+'_success', 1)
    return True


# main init
init_data_space(mainlog, flush=False)



# ******************************************非api直接调用函数分界线******************************************

# 删库重来
def restart_table():
    try:
        restart_all(mainlog)
        init_data_space(mainlog, False)
        return {"msg": "删表重建完成"}
    except Exception:
        traceback.print_exc(file=open('GaoKao2022/log/0.log', 'a'))
        return {"msg": "删除表格失败"}


# 清理redis缓存，重新加载
def reset_redis():
    try:
        init_data_space(mainlog, True)
        return {"msg": "缓存清理完成"}
    except Exception:
        traceback.print_exc(file=open('GaoKao2022/log/0.log', 'a'))
        return {"msg": "缓存清理失败"}


# 删除指定省份的数据
def del_province(province):
    try:
        del_sql_province(province)
        return {"msg": "删表完成"}
    except Exception:
        traceback.print_exc(file=open('GaoKao2022/log/0.log', 'a'))
        return {"msg": "删除表格失败"}


# 重设表格字段类型
def reset_table():
    try:
        set_table_type()
        return {"msg": "重新设置完成"}
    except Exception:
        traceback.print_exc(file=open('GaoKao2022/log/0.log', 'a'))
        return {"msg": "重新设置失败"}


# rule表重来
def restart_rule():
    try:
        delete_rule_table()
    except Exception:
        traceback.print_exc(file=open('GaoKao2022/log/0.log', 'a'))
        return {"msg": "删除表格失败"}
    try:
        try_creat_rule_table(mainlog)
        return {"msg": "删表重建完成"}
    except Exception:
        traceback.print_exc(file=open('GaoKao2022/log/0.log', 'a'))
        return {"msg": "创建表格失败"}


# 筛选数据
def select_df(province_id, batch_text):
    # 省份筛选
    global BATCH_LIST, CONFIG
    if str(province_id) not in BATCH_LIST:
        return {"msg": "省份数据未初始化", "code": -4}
    batchs = list(BATCH_LIST.smembers(str(province_id)))
    if len(batchs)==0:
        return {"msg": "省份数据为空", "code": -4}
    # 寻找批次
    batch_select = ""
    if batch_text['batch_norm']!="":
        if batch_text['batch_norm'] not in batchs:
            return {"msg": "batch_norm %s error"%batch_text['batch_norm'], "code": -5}
        else:
            batch_select = batch_text['batch_norm']
    elif batch_text['batch_plan']!="":
        for b in batchs:
            if batch_text['batch_plan'] in pickle.loads(CONFIG.get('%s_%s'%(province_id, b)))['goal_batch']:
                batch_select = b
        if batch_select=="":
            return {"msg": "batch_plan %s error" % batch_text['batch_plan'], "code": -5}
    elif batch_text['batch_fsx']!="":
        for b in batchs:
            if batch_text['batch_fsx'] == pickle.loads(CONFIG.get('%s_%s'%(province_id, b)))['goal_sf_batch']:
                batch_select = b
        if batch_select=="":
            return {"msg": "batch_fsx %s error" % batch_text['batch_fsx'], "code": -5}
    else:
        return {"msg": "batch error", "code": -5}
    return "%s_%s"%(str(province_id), batch_select)


# 预测主函数
def predict(province_id, wenli, batch_text, score, rank, select_list, detail, college_province):
    key = select_df(province_id, batch_text)
    if type(key) == dict:
        return key
    global DF_DATA, CONFIG
    cfg = pickle.loads(CONFIG.get(key))
    df = pickle.loads(DF_DATA.get(key))
    df = predict_prob(cfg, df, wenli, score, rank, select_list, detail, college_province)
    return {'data': df.to_dict(orient="records"), 'mode': cfg['mode']}


# 预测院校概率主函数
def predict_college(province_id, wenli, batch_text, score, rank, college_id):
    key = select_df(province_id, batch_text)
    if type(key) == dict:
        return key
    global DF_DATA, CONFIG
    cfg = pickle.loads(CONFIG.get(key))
    df = pickle.loads(DF_DATA.get(key))
    years, prob, tp = predict_college_prob(cfg, df, wenli, score, rank, college_id)
    return {
        "plan_year": years,
        "college_prob": prob,
        "type": tp
    }


# 获取批次名称匹配表
def get_batch_info(province_id):
    global BATCH_LIST, CONFIG
    if str(province_id) not in BATCH_LIST:
        return {"msg": "省份数据未初始化", "code": -4}
    if BATCH_LIST.scard(str(province_id))==0:
        return {"msg": "省份没有数据", "code": -4}
    batchs = list(BATCH_LIST.smembers(str(province_id)))
    batch_all = []
    for batch in list(BATCH_LIST.smembers(str(province_id)+'_all')):
        if batch not in batchs:
            d = {
                'batch_norm': batch,
                'enable': False,
            }
            batch_all.append(d)
    for batch in batchs:
        key = "%s_%s"%(province_id, batch)
        config = pickle.loads(CONFIG.get(key))
        d = {
            'batch_norm': batch,
            'enable': True,
            'batch_plan': config['goal_batch'],
            'batch_fsx': config['goal_sf_batch'],
            'mode': config['mode'],
            'goal_years': int(config['goal_years']),
            'gaozhi': int(config['gaozhi']),
            'cengci': int(config['cengci']),
            'num_school': int(config['num_school']),
            'num_sp': int(config['num_sp']),
            'wenli': int(config['wenli']),
        }
        for k in config.keys():
            if ('data_' in k):
                d[k] = config[k]
        batch_all.append(d)
    return {'batch_info': batch_all}


# 初始化所有数据
def start_all_data(top, end, replace=False):
    global BATCH_LIST
    for i in range(top, end+1):
        if replace:
            start_province(i)
        else:
            if str(i)+'_all' not in BATCH_LIST:
                start_province(i)
            else:
                pass
    return {'msg': 'COMPLETED!'}


# 初始化指定省份数据
def start_province(province_id):
    global ALL_SIGN, BATCH_LIST, DF_DATA, CONFIG
    if int(ALL_SIGN.get(str(province_id)+'_init')):
        return {'msg': '初始化程序正在运行中!'}
    ALL_SIGN.set(str(province_id)+'_init', 1)
    try:
        rdict, batch_all = init_data_province(province_id)
        for b in batch_all:
            BATCH_LIST.sadd(str(province_id)+'_all', b)
        for b in list(rdict.keys()):
            BATCH_LIST.sadd(str(province_id), b)
        for batch in rdict.keys():
            key = "%s_%s"%(str(province_id), batch)
            DF_DATA.set(key, pickle.dumps(rdict[batch]['data']))
            CONFIG.set(key, pickle.dumps(rdict[batch]['cfg']))
    except Exception:
        # TODO: 错误日志还没有保存在redis里，只是保存本地
        traceback.print_exc(file=open('GaoKao2022/log/%s.log'%province_id, 'a'))
        mainlog.info("初始化数据%s失败"%province_id)

    ALL_SIGN.set(str(province_id)+'_init', 0)
    return {'msg': 'COMPLETED!'}


# 更新指定省份数据
def update_province_data(province_id):
    global ALL_SIGN, BATCH_LIST, CONFIG, DF_DATA
    if int(ALL_SIGN.get(str(province_id)+'_update')):
        return {'msg': '更新程序正在运行中!'}
    ALL_SIGN.set(str(province_id)+'_update', 1)
    try:
        data, batch_all = updata_data_province(province_id)
        for b in batch_all:
            BATCH_LIST.sadd(str(province_id)+'_all', b)
        if len(data.keys())>0:
            for batch in data.keys():
                BATCH_LIST.sadd(str(province_id), batch)
                key = "%s_%s"%(str(province_id), batch)
                DF_DATA.set(key, pickle.dumps(data[batch]['data']))
                CONFIG.set(key, pickle.dumps(data[batch]['cfg']))
        ALL_SIGN.set(str(province_id)+'_success', 1)
    except Exception:
        traceback.print_exc(file=open('GaoKao2022/log/%s.log'%province_id, 'a'))
        mainlog.info("更新%s号省份失败，详情请查看该省份日志"%province_id)
        ALL_SIGN.set(str(province_id)+'_success', 0)
    ALL_SIGN.set(str(province_id)+'_update', 0)
    return {'msg': 'COMPLETED!'}


# 更新所有状态为不正常省份的数据
def update_all(top, end, province_list):
    goal_province = range(top, end+1)
    if len(province_list)>0:
        goal_province = province_list
    for province_id in goal_province:
        stat = get_province_stat(province_id)
        if not stat['initing'] and not stat['creating']:
            update_province_data(province_id)
    return {'msg': 'COMPLETED!'}


# 获取指定省份日志
def get_province_log(province_id, file=False):
    if file:
        file = 'GaoKao2022/log/%s.log'%province_id
        f = open(file, 'r', encoding='utf8')
        text = f.read()
        f.close()
        return {'log': text}
    else:
        text = LOG_DATA.get(str(province_id))
        return {'log': text}


# 获取冲稳保的分割线
def get_split_cwb():
    return {
        'c': split_c,
        "cw": split_cw,
        'wb': split_wb
    }


# 获取省份的数据状态
def get_province_stat(province):
    result = dict()
    if province<=0:
        for i in range(1, 31):
            result[str(i)] = get_province_stat(i)
    else:
        result['batch_ok'] = []
        result['batch_fail'] = []
        global BATCH_LIST, ALL_SIGN
        if str(province)+'_all' in BATCH_LIST:
            result['init'] = True
            batch_all = list(BATCH_LIST.smembers(str(province)+'_all'))
            if str(province) in BATCH_LIST:
                batch_ok = list(BATCH_LIST.smembers(str(province)))
                for b in batch_all:
                    if b in batch_ok:
                        result['batch_ok'].append(b)
                    else:
                        result['batch_fail'].append(b)
            else:
                result['batch_fail'] = batch_all
        else:
            result['init'] = False
        result['create'] = False if int(ALL_SIGN.get(str(province)+'_success'))==0 else True
        result['province_id'] = province
        result['province'] = id2province(province)
        result['creating'] = True if int(ALL_SIGN.get(str(province)+'_update')) else False
        result['initing'] = True if int(ALL_SIGN.get(str(province)+'_init')) else False
        result['exceling'] = True if int(ALL_SIGN.get(str(province)+'_excel')) else False
        result['excel'] = True if str(province) in DF_EXCEL else False

    return result


# 获取指定省份的院校榜单
def get_school_rank(province_id):
    global ALL_SIGN, DF_EXCEL
    if int(ALL_SIGN.get(str(province_id)+'_excel')):
        return {'msg': '生成程序正在运行中!'}
    ALL_SIGN.set(str(province_id) + '_excel', 1)
    try:
        bangdan = get_bangdan(province_id)
        DF_EXCEL.set(str(province_id), pickle.dumps(bangdan))
    except Exception:
        traceback.print_exc(file=open('GaoKao2022/log/rank%s.log'%province_id, 'a'))
        mainlog.info("更新%s号省份失败，详情请查看该省份日志"%province_id)
        ALL_SIGN.set(str(province_id) + '_excel', 0)
        return {'msg': '失败!'}
    ALL_SIGN.set(str(province_id) + '_excel', 0)
    return {'msg': '完成!'}


# 下载院校榜单
def download_school_rank(province_id):
    global ALL_SIGN, DF_EXCEL
    if str(province_id) in DF_EXCEL:
        result = pickle.loads(DF_EXCEL.get(str(province_id)))
        filename = download_excel(result)
        return {
            'ok': True,
            'filename': filename
        }
    else:
        return {
            'ok': False
        }
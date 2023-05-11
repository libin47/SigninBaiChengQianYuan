# -*- coding: utf-8 -*-
import logging
from .setting import SQLGoal, TableGoalSchool, TableGoalSp, TableGoalRule
from .base import select_type, cols_school, cols_school_old, cols_sp, cols_sp_old,\
    keys_sp_plan, keys_school_plan
from .rule_util import config, varchar_length
import pandas as pd
from mysql.connector import connect
from sqlalchemy import create_engine
import time


def get_connect(SQL):
    con = create_engine(r'mysql+pymysql://{username}:{password}@{host}:{port}/{databases}'.format(
        username=SQL['user'], password=SQL['password'], host=SQL['host'],
        port=SQL['port'], databases=SQL['database']))
    return con


# 查看目标两个表是否存在
def goal_table_exist():
    db = connect(**SQLGoal)
    sql_text = "show tables"
    df = pd.read_sql(sql_text, db)
    db.close()
    if (TableGoalSchool in df.transpose().values) and (TableGoalSp in df.transpose().values):
        return True
    else:
        return False


# 根据mode确定目标写入表
def get_table(mode):
    # 确定用哪个表
    if mode in ['school']:
        table = TableGoalSchool
    elif mode in ['sp', 'group']:
        table = TableGoalSp
    else:
        logging.error('错误的mode！')
    return table


# 获取表中的数据类型
def get_type(col):
    if col in select_type.keys():
        if select_type[col]=='strs':
            return ', %s VARCHAR(64) NOT NULL DEFAULT ""'%col
        elif select_type[col]=='str':
            return ', %s VARCHAR(512) NOT NULL DEFAULT ""'%col
        elif select_type[col]=='int':
            return ', %s INT NOT NULL DEFAULT -1'%col
        elif select_type[col]=='float':
            return ', %s FLOAT NOT NULL DEFAULT -1'%col
    else:
        for c in select_type.keys():
            if c == col[:len(c)]:
                if select_type[c] == 'strs':
                    return ', %s VARCHAR(%s) NOT NULL DEFAULT ""'%(col, varchar_length['strs'])
                if select_type[c] == 'str':
                    return ', %s VARCHAR(%s) NOT NULL DEFAULT ""'%(col, varchar_length['str'])
                elif select_type[c] == 'int':
                    return ', %s INT NOT NULL DEFAULT -1'%col
                elif select_type[c] == 'float':
                    return ', %s FLOAT NOT NULL DEFAULT -1' % col
    print("????????")


# 重设字段类型
def set_table_type_sub(planlist, datalist, wenliyear, table):
    db = connect(**SQLGoal)
    cursor = db.cursor()
    txt = "ALTER TABLE {table} MODIFY COLUMN id BIGINT NOT NULL auto_increment;".format(table=table)
    cursor.execute(txt)
    db.commit()
    for col in planlist:
        txt = get_type(col).replace(',', 'ALTER TABLE {table} MODIFY COLUMN'.format(table=table)) + ';'
        cursor.execute(txt)
        db.commit()
    for i in range(config['year_old']):
        for col in datalist:
            year = config['years'] - 1 - i
            cols = col + '_%s'%year
            txt = get_type(cols).replace(',', 'ALTER TABLE {table} MODIFY COLUMN'.format(table=table)) + ';'
            cursor.execute(txt)
            db.commit()
            if i+1>wenliyear:
                txt = get_type(cols + '_wen').replace(',', 'ALTER TABLE {table} MODIFY COLUMN'.format(table=table)) + ';'
                cursor.execute(txt)
                txt = get_type(cols + '_li').replace(',', 'ALTER TABLE {table} MODIFY COLUMN'.format(table=table)) + ';'
                cursor.execute(txt)
                db.commit()
    db.close()
    return True


def set_table_type():
    set_table_type_sub(cols_school, cols_school_old, config['wenli_year'], TableGoalSchool)
    set_table_type_sub(cols_sp, cols_sp_old, config['wenli_year'], TableGoalSp)


# 根据给定条件创建表
def creat_goal_sub(planlist, datalist, wenliyear, table):
    txt = ""
    for col in planlist:
        txt = txt + get_type(col)
    for i in range(config['year_old']):
        for col in datalist:
            year = config['years'] - 1 - i
            cols = col + '_%s'%year
            txt = txt + get_type(cols)
            if i+1>wenliyear:
                txt = txt + get_type(cols + '_wen')
                txt = txt + get_type(cols + '_li')
    sql = "CREATE TABLE {table} (" \
          "id BIGINT NOT NULL PRIMARY KEY auto_increment" \
          "{columns}" \
          ");".format(table=table, columns=txt)
    db = connect(**SQLGoal)
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    db.close()
    return True


# 创建表
def creat_table():
    creat_goal_sub(cols_school, cols_school_old, config['wenli_year'], TableGoalSchool)
    creat_goal_sub(cols_sp, cols_sp_old, config['wenli_year'], TableGoalSp)


# 删除
def delete_table():
    db = connect(**SQLGoal)
    cursor = db.cursor()
    cursor.execute("DROP TABLE {table}".format(table=TableGoalSchool))
    cursor.execute("DROP TABLE {table}".format(table=TableGoalSp))
    cursor.execute("DROP TABLE {table}".format(table=TableGoalRule))
    db.commit()
    db.close()
    return True


def delete_rule_table():
    db = connect(**SQLGoal)
    cursor = db.cursor()
    cursor.execute("DROP TABLE {table}".format(table=TableGoalRule))
    db.commit()
    db.close()
    return True


# 设置主键
def set_primary(log):
    db = connect(**SQLGoal)
    cursor = db.cursor()
    try:
        cursor.execute("ALTER TABLE {table} ADD id INT NOT NULL auto_increment PRIMARY KEY FIRST".format(table=TableGoalSchool))
    except:
        log.warning("设置主键失败")
    try:
        cursor.execute("ALTER TABLE {table} ADD id INT NOT NULL auto_increment PRIMARY KEY FIRST".format(table=TableGoalSp))
    except:
        log.warning("设置主键失败")
    db.commit()
    db.close()


# 删除指定表指定id的数据
def del_sql_base(table, ids):
    db = connect(**SQLGoal)
    cursor = db.cursor()
    idss = [str(int(i)) for i in ids]
    id_txt = '(' + ','.join(idss) + ')'
    del_text = "DELETE FROM {table} WHERE id in {ids}".format(
        table=table, ids=id_txt)
    cursor.execute(del_text)
    db.commit()
    db.close()
    return True


# 删除一个省指定不在批次
def del_sql_not_batch(province_id, batchnot, log):
    db = connect(**SQLGoal)
    cursor = db.cursor()
    batch_txt = '("' + '","'.join(batchnot) + '")'
    # 删除院校表中
    del_text = "DELETE FROM {table} WHERE province_id={provice} AND batch_text not in {batch}".format(
        table=TableGoalSchool, provice=province_id, batch=batch_txt)
    cursor.execute(del_text)
    db.commit()
    # 删除专业表中
    del_text = "DELETE FROM {table} WHERE province_id={provice} AND batch_text not in {batch}".format(
        table=TableGoalSp, provice=province_id, batch=batch_txt)
    cursor.execute(del_text)
    db.commit()
    log.info("[MYSQL]清除其他批次数据")

    db.close()
    return True


# 删除一个省所有
def del_sql_province(province_id):
    db = connect(**SQLGoal)
    cursor = db.cursor()
    del_text = "DELETE FROM {table} WHERE province_id={provice}".format(
        table=TableGoalSchool, provice=province_id)
    cursor.execute(del_text)
    db.commit()

    del_text = "DELETE FROM {table} WHERE province_id={provice}".format(
        table=TableGoalSp, provice=province_id)
    cursor.execute(del_text)
    db.commit()
    db.close()
    return True


# 删除一个省指定批次
def del_sql_batch(province_id, batch, log):
    # set_primary(log)
    db = connect(**SQLGoal)
    cursor = db.cursor()

    # 删除院校表中
    del_text = "DELETE FROM {table} WHERE province_id={provice} AND batch_text='{batch}'".format(
        table=TableGoalSchool, provice=province_id, batch=batch)
    cursor.execute(del_text)
    db.commit()
    log.info("[MYSQL]清除院校表中已有内容")

    # 删除专业表中
    del_text = "DELETE FROM {table} WHERE province_id={provice} AND batch_text='{batch}'".format(
        table=TableGoalSp, provice=province_id, batch=batch)
    cursor.execute(del_text)
    db.commit()
    log.info("[MYSQL]清除专业表已有内容")

    db.close()
    return True


# 删除掉数据中不在表中列的字段
def clear_cols_for_sql(df, table, log):
    db = connect(**SQLGoal)
    tp = pd.read_sql("SELECT * FROM %s LIMIT 1"%table, db)
    db.close()
    df_cols = df.columns
    sqlcols = tp.columns
    remove_list = []
    for col in df_cols:
        if col not in sqlcols:
            remove_list.append(col)
            df.drop(col, axis=1, inplace=True)
    if len(remove_list)>0:
        log.warning("[SQL]数据表不包含以下列:%s"%remove_list)
    return df


# 更新数据
def update_sql_base(df, table):
    con = get_connect(SQLGoal)
    table_name = 'temp_table_%s'%int(time.time()*1000000)
    df.to_sql(table_name, con=con, if_exists='replace', index=False)

    db = connect(**SQLGoal)
    cursor = db.cursor()
    replace_text = "REPLACE INTO {table}({colmuns}) SELECT * FROM {table_temp}".format(
        table=table, table_temp=table_name, colmuns=','.join(list(df.columns))
    )
    cursor.execute(replace_text)
    cursor.execute("DROP TABLE {table}".format(table=table_name))
    db.commit()
    db.close()
    return True


# 保存该批次的内容
def save2mysql(df, cfg, log):
    mode = cfg['mode']
    # 连接数据库
    con = get_connect(SQLGoal)
    table = get_table(mode)
    # 清理数据列
    df = clear_cols_for_sql(df, table, log)
    # 获取已有数据
    df_sql = data_is_exist(cfg['province_id'], cfg['batch_text'], mode)
    # log
    log.info('[%s]保存中:需保存%s条数据，数据库中存在%s条数据'%(cfg['batch_text'], len(df), len(df_sql)))
    # 保存
    if len(df_sql) == 0:
        df.to_sql(table, con=con, if_exists='append', index=False)
    else:
        keys = keys_school_plan if mode=='school' else keys_sp_plan
        table = TableGoalSchool if mode=='school' else TableGoalSp
        df_sql = df_sql[keys + ['id']]
        # check
        if len(df)!=len(df.drop_duplicates(keys, keep='first', inplace=False)):
            log.error("GROUP后数量变化，请筛查原因并及时更新，防止数据库保存多条重复数据")
        if len(df_sql)!=len(df_sql.drop_duplicates(keys, keep='first', inplace=False)):
            log.error("SQL数据GROUP后数量变化，请筛查原因并及时更新，防止数据库保存多条重复数据")
            df_sql_group = df_sql.drop_duplicates(keys, keep='first', inplace=False)
            df = pd.merge(df, df_sql_group, on=keys, how='outer')
            df_insert = df[(pd.isnull(df.id)) & (~pd.isnull(df.province_id))]
            df_replace = df[(~pd.isnull(df.id)) & (~pd.isnull(df.province_id))]
            df_remove = df_sql.copy()
            log.info("[SQL]%s条新增、%s条替换或新增、%s条删除" % (len(df_insert), len(df_replace), len(df_remove)))
        else:
            df = pd.merge(df, df_sql, on=keys, how='outer')
            # 有则更新 无则插入 原来有现在没了的删除
            df_insert = df[(pd.isnull(df.id))&(~pd.isnull(df.province_id))]
            df_replace = df[(~pd.isnull(df.id))&(~pd.isnull(df.province_id))]
            df_remove =df[(pd.isnull(df.province_id))&(~pd.isnull(df.id))]
            log.info("[SQL]%s条新增、%s条更新、%s条删除" % (len(df_insert), len(df_replace), len(df_remove)))
        # remove
        if len(df_remove)>0:
            del_sql_base(table, list(df_remove.id))
        # insert
        if len(df_insert)>0:
            df_insert.to_sql(table, con=con, if_exists='append', index=False)
        # replace
        if len(df_replace)>0:
            update_sql_base(df_replace, table)
    log.info("[保存]：数据已保存至数据库中")
    return True


# 获取数据
def data_is_exist(province, batch, mode):
    db = connect(**SQLGoal)
    table = get_table(mode)
    sql = "SELECT * FROM {table} WHERE province_id={province} AND batch_text='{batch}'".format(
        table=table,
        province=province,
        batch=batch)
    df = pd.read_sql(sql, db)
    db.close()
    return df


# 根据id获取全部数据——用于演示系统 临时使用
def get_data_by_id(df, mode, group):
    db = connect(**SQLGoal)
    table = get_table(mode)

    idlist = list(df.id)
    if len(idlist)==0:
        return df
    idlist = '(' + ','.join([str(i) for i in idlist]) + ')'

    cols_school = ["id", "college_id", "school_code", "schoolname", "minscore_rank_2019", "minscore_rank_2020", "minscore_rank_2021", "predict_rank"]
    cols_sp = ["id", "college_id", "school_code", "schoolname", "minscore_rank_2019", "minscore_rank_2020", "minscore_rank_2021", "predict_rank",
               "sp_name", "sp_code", "demand", "sg_name"]

    sql = "SELECT {col} FROM {table} WHERE id in {idlist}".format(
        col=','.join(cols_school if mode=='school' else cols_sp),
        table=table,
        idlist=idlist)
    result = pd.read_sql(sql, db)
    db.close()
    df = pd.merge(df, result, on=['id'], how='left')

    if (mode=='group') and group:
        df = df.groupby(by=["college_id", "school_code", "schoolname", "demand", "sg_name"], as_index=False).agg({
            "minscore_rank_2020": max, "minscore_rank_2019": max, "minscore_rank_2021":max, "predict_rank":max, "prob":max
        })
    return df



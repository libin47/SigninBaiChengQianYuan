# -*- coding: utf-8 -*-
import re
import pandas as pd
from .setting import TableMajor, SQLMajor
from mysql.connector import connect


# 获取专业code表
def get_sp_list():
    db = connect(**SQLMajor)
    sql_text = """
    SELECT `code`, `name` spname, cengci, level
    FROM %s
    WHERE stat=1 and cengci<3 and cengci>0
    ORDER BY cengci,zhijiao
    """%TableMajor
    df_code = pd.read_sql(sql_text, db)
    db.close()
    return df_code


df_sp_code = get_sp_list()


# 获取专业的major_code
def get_sp_code(df, cengci):
    df_code = df_sp_code.copy()
    if cengci>0:
        df_code = df_code[df_code.cengci==cengci]
    df_3 = df_code[df_code.level == 3][['code', 'spname']]
    df_2 = df_code[df_code.level == 2][['code', 'spname']]
    df_1 = df_code[df_code.level == 1][['code', 'spname']]

    df_0 = pd.concat([df_3, df_2, df_1], axis=0)
    df_0 = df_0.drop_duplicates('spname', keep='first', inplace=False)
    df_0 = df_0.rename({'spname': 'spname_name'}, axis=1)
    # merge
    df = pd.merge(df, df_0, on=['spname_name'], how='left')
    # df[.., code]
    df['code'] = df['code'].apply(lambda x: '' if pd.isnull(x) else x)
    df['code_2'] = df['code'].apply(lambda x: '' if len(x)<4 else x[:4])
    df['code_1'] = df['code'].apply(lambda x: '' if len(x)<2 else x[:2])
    # df_2 = df_2.rename({'code':'code_2', 'spname':'spname_2'}, axis=1).groupby(by='code_2', as_index=False).agg({'spname_2':my_first})
    # df = pd.merge(df, df_2, on=['code_2'], how='left')
    # df_1 = df_1.rename({'code':'code_1', 'spname':'spname_1'}, axis=1).groupby(by='code_1', as_index=False).agg({'spname_1':my_first})
    # df = pd.merge(df, df_1, on=['code_1'], how='left')
    # # df[..,code,code_1,spname_1,code_2,spname_2]
    # df.drop(['code', 'code_1', 'code_2'], axis=1, inplace=True)
    # df['spname_1'] = df['spname_1'].apply(lambda x: '' if pd.isnull(x) else x)
    # df['spname_2'] = df['spname_2'].apply(lambda x: '' if pd.isnull(x) else x)
    df.rename({'code':'major_code', 'code_1':'major_code_1', 'code_2':'major_code_2'}, axis=1, inplace=True)
    return df


spname_cols = ['spname_name', 'spname_base', 'spname_sem', 'spname_extra', 'spname_sub']

'''
专业说明类：特殊班种 专项 师范类 定向 高收费专业 年制 子专业 所属方向 分流说明  紧缺专业 培养方案 只招专业志愿(单列志愿)  预科
招生要求类：男女要求 身体要求 能力基础要求 语种要求 单科成绩限制 身份要求(少数民族) 额外考试 面向地区招生
去向：面向地区就业 走读 
开设单位说明：中外合作 校企合作 联合培养 合作培养 校区 培养基地/计划  学费标准 授予学位 授课学院  本硕博连读(贯通培养) 授课语言 专业补助
15 地方专项 中外合作 校企合作 *预科班
19 中外合作 师范 面向地区 类 班 学院 年制 法学限定 授予学位 校区+中大限定  专项/定向    
*子专业或包含专业 方向
可能情况：
试验班(方向) 试验班类(方向)：方向包括 专业 专业类 班 学堂 计划
民族班(方向) 预科班(方向)
'''
def clear_spname(df):
    特殊班, 中外, 师范, 面向, 学院,  \
    法学限定, 授予学位, 校区, 定向, 专项, \
    民族, 包含专业, 方向, 专业组, 年制 = ['' for i in range(15)]

    # 正则化
    spname = df['sp_name'].replace('（', '(').replace('）', ')').replace(' ', '')
    remark = df['remark'].replace('（', '(').replace('）', ')').replace(' ', '')
    remark = re.sub('常规批第[123]次', '', remark)
    remark = re.sub('--', '', remark)
    # 处理专业名
    spname_list = re.split('\(|\[', spname)
    # No.1:  无备注,专业名无括号:  直接返回
    if len(spname_list) == 1 and len(remark) == 0:
        if 'semester' in df.keys():
            年制 = get_number_chinese(df['semester'])
        return [spname_list[0], '', 年制, '', '']
    spname_name = spname_list[0]
    # (No.2: 无备注，专业名有括
    # 算了，直接其他吧
    # 抽取所有备注 去重为一个list
    spname_ = re.sub('\)$|^\(', '', spname[len(spname_list[0]):])
    remark_list = re.split('\)\(|\;|；|,|，|。|_|\n| ', spname_)
    remark_list.extend(re.split('\)\(|\;|；|,|，|。|_|\n| ', remark))
    remark_list = sorted(set(remark_list), key=remark_list.index)
    # 专业清单以做对照
    df_code = df_sp_code.copy()
    sp_list = list(df_code.spname)
    # 依次对其中每一条进行判断
    for sth in remark_list:
        sth = re.sub('\)|\(|\:|：', '', sth)
        # 假设每一条只能提供一个关键信息
        if (re.search('^含', sth) or (not re.search('色盲', sth) and (re.search('、', sth) or re.search('专业', sth)))) and is_in_splist(sth, sp_list):
            包含专业 = re.sub('^包含|^含|专业$','',sth)
        elif re.search('中外|中美|中日|国际课程|中英|中欧|国际班|马来西亚|中澳', sth):
            中外 = '中外合作'
        elif re.search('闽台', sth):
            中外 = '闽台合作'
        elif re.search('班$', sth) and not re.search('^含', sth):
            特殊班 = sth
        elif re.search('少数民族', sth):
            民族 = sth
        elif re.search('师范', sth) and not re.search('非师范', sth):
            师范 = '师范类'
        elif re.search('^面向|市内$', sth):
            面向 = sth
        elif re.search('市外$', sth):
            continue
        elif re.search('院$|堂$', sth) and not re.search('地点', sth):
            学院 = sth
        elif (spname_name=='法学') and (re.search('法$', sth)):
            法学限定 = sth
        elif (sth=='工学') or (sth=='理学') or (sth=='医学'):
            授予学位 = sth
        elif (sth=='珠海') or (sth=='广州') or (sth=='深圳'):
            校区 = sth
        elif re.search('定向', sth) and not re.search('非定向', sth):
            定向 = sth
        elif re.search('专项', sth) and not re.search('非专项', sth):
            专项 = sth
        # 因为有3+2中澳班之类的东西，所以年制判断放中外合作之后就比较省力
        elif re.search('年制|一体化', sth):
            sth = sth.replace('8', '八').replace('7', '七').replace('6', '六').replace('5', '五').replace('4', '四').replace('3', '三').replace('+', '加')
            if re.search('八|五加三', sth):
                年制 = '八'
            elif re.search('七', sth):
                年制 = '七'
            elif re.search('六', sth):
                年制 = '六'
            elif re.search('五', sth):
                年制 = '五'
            elif re.search('三加二', sth):
                年制 = '五'
        elif re.search('5\+3|本硕博', sth):
            年制 = '八'
        elif (方向=='') and (re.search('方向$', sth)):
            方向 = re.sub('方向$','', sth)
        else:
            if (方向 == ''):
                if ((spname_name[-1:] == '班') or (spname_name[-2:] == '班类')) and (sth==remark_list[0]):
                    方向 = sth
                if is_in_splist(sth, sp_list):
                    方向 = re.sub('^包含|^含|专业$', '', sth)
    # 判断根据字段判断学制和专业组
    if 'semester' in df.keys():
        年制 = get_number_chinese(df['semester'])
    return [spname_name, 特殊班+学院+中外+师范+面向+法学限定+授予学位+校区+定向+专项+民族, 年制, 方向, 包含专业]


# 数字转汉字
def get_number_chinese(num):
    if num<=4:
        return ''
    clist = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    if num<11:
        return clist[num]
    else:
        return ''

# 判断名字是否在专业列表中
def is_in_splist(sth, sp_list):
    sth = re.sub('^含|专业$','',sth)
    sth = re.split('、', sth)
    for sp in sth:
        if sp in sp_list:
            return True
    return False


# xx中的remark整理
def clear_remark(remark):
    remark = '' if pd.isnull(remark) else str(remark)
    remark_list = re.split('\)\(|\;|；|,|，|。|_|\n| ', remark)
    中外, 民族, 预科, 定向 = "", "", "", ""
    for sth in remark_list:
        if re.search('中外|中美|中日|闽台|中英|中欧|国际班|马来西亚|中澳', sth):
            中外 = '中外合作'
        elif re.search('民族', sth):
            民族 = sth
        elif re.search('预科', sth):
            预科 = sth
        elif re.search('定向', sth) and not re.search('非定向', sth):
            定向 = sth
    return 中外+民族+预科+定向

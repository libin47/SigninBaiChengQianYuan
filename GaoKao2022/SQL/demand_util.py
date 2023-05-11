# -*- coding: utf-8 -*-


# 处理demand
def clear_demand(demand):
    if ('不限' in demand) or ('无限制' in demand):
        return ['', '', '', '']
    x = []
    if ('物理' in demand) or ('物' in demand and '生物' not in demand):
        x.append('物理')
    if ('历' in demand) or ('史' in demand):
        x.append('历史')
    if ('政' in demand) or ('治' in demand):
        x.append('政治')
    if ('地' in demand):
        x.append('地理')
    if ('生' in demand):
        x.append('生物')
    if ('化' in demand):
        x.append('化学')
    if ('技' in demand) or ('术' in demand):
        x.append('技术')
    if len(x)<3:
        x.extend(['' for i in range(3-len(x))])
    # TODO: 4种而且还是+的情况需要处理
    elif len(x)>3:
        return ['', '', '', '']
    j = ''
    if ('和' in demand) or ('+' in demand) or ('且' in demand):
        j = '+'
    x.append(j)
    return x


# 判断demand是否符合
def demand_jg(df, user):
    demand_1_isnull = (df['demand_1'] == '')
    demand_2_isnull = (df['demand_2'] == '')
    demand_3_isnull = (df['demand_3'] == '')
    demand_c = (df['demand_concat'] == '')
    demand_1_indf, demand_2_indf, demand_3_indf = False, False, False
    for d in user:
        demand_1_indf = (demand_1_indf | (df['demand_1'] == d))
        demand_2_indf = (demand_2_indf | (df['demand_2'] == d))
        demand_3_indf = (demand_3_indf | (df['demand_3'] == d))
    b = (demand_1_isnull & demand_2_isnull & demand_3_isnull) | (demand_2_isnull & demand_3_isnull & demand_1_indf) |\
        (demand_3_isnull & (demand_1_indf | demand_2_indf) & demand_c) |\
        ((demand_1_indf | demand_2_indf | demand_3_indf) & demand_c) |\
        (demand_3_isnull & demand_1_indf & demand_2_indf & ~demand_c) |\
        (demand_1_indf & demand_2_indf & demand_3_indf & ~demand_c)
    return b
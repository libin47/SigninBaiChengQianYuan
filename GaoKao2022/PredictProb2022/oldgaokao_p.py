# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:47:35 2021

@author: Thinkpad
"""


import pandas as pd
import pickle
from scipy.stats import norm
import numpy as np
import math

import warnings
warnings.filterwarnings('ignore')
# import os
# os.chdir(r'C:\Users\Thinkpad\Desktop\xm\predict_score')

def probability_old_gaokao(data,score,rank,province,wenli, cengci, showall=False):
    '''
    适用省份:河北,山西,内蒙古,辽宁,吉林,黑龙江,上海,浙江,安徽,福建,江西,河南,湖北,湖南,广东,广西,甘肃,陕西,新疆,青海,宁夏,重庆,四川,贵州,云南,西藏
    ID:3,4,5,6,7,8,9,11,12,13,14,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31
    Parameters
    ----------
    data:dataframe
        整个院校df表
    score:int
    rank:int
    province:int
    wenli:int
    showall:bool,optional
        是否展示所有结果。false会筛掉概率小于1%和没有数据的结果,true会返回所有结果。默认false
    
    Returns
    -------
    data:dataframe
        整个院校df表，增加2021年的预测录取概率
    '''
    if rank<1|score<1:
        return '??????'
    data=data[data['wenli']==wenli]
    if (province==24): # 新疆用分数预测  or (province==4 and cengci==2)
        score2022=data[['predict_minscore','predict_minscore_std']]
        data['probability']=np.around(norm.cdf(score,loc=score2022['predict_minscore'].values,scale=score2022['predict_minscore_std'].values),3)
        # data['probability']=score2021.apply(lambda x:1-norm.cdf(score, loc=x[0], scale=x[1]),axis=1)
        data=data.sort_values(by=['probability','predict_minscore'],ascending=[True,False])
    else:#其它用排名
        xian=data[data['batch_score']!=-1]['batch_score'].unique()#找出不是-1的分数线
        xian=xian[(score-xian<30)&(score-xian>=0)]#范围是0-29
        if len(xian)==1 and data['batch_rank'].unique()[0]>0:#如果分数在分数线附近
            batch_renshu=data[data['batch_score']==xian[0]]#存在上线数据
            if len(batch_renshu)>0:
                #上线的院校用排名和排名百分比预测
                rank_p=rank/batch_renshu['batch_rank'].values[0]#计算排名百分位
                result1=data[data['batch_score']==xian[0]]#将属于该线的院校提取出来
                #排名百分比
                rank_p2022=result1[['predict_rank_p','predict_rank_p_std']]
                result1_p1=1-norm.cdf(rank_p,loc=rank_p2022['predict_rank_p'].values,scale=rank_p2022['predict_rank_p_std'].values)
                #排名
                rank2022=result1[['predict_rank','predict_rank_std']]
                result1_p2=1-norm.cdf(rank,loc=rank2022['predict_rank'].values,scale=rank2022['predict_rank_std'].values)
                e=score-xian[0]
                w=(math.tanh((e)/30*4-2)+1)/2
                result1['probability']=np.around((1-w)*result1_p1+w*result1_p2,3)
                # result1['probability']=rank_p2022.apply(lambda x:1-norm.cdf(rank_p, loc=x[0], scale=x[1]),axis=1)
                #其它院校用排名预测
                result2=data[data['batch_score']!=xian[0]]
                rank2022=result2[['predict_rank','predict_rank_std']]
                result2['probability']=np.around(1-norm.cdf(rank,loc=rank2022['predict_rank'].values,scale=rank2022['predict_rank_std'].values),3)
                # result2['probability']=rank2022.apply(lambda x:1-norm.cdf(rank, loc=x[0], scale=x[1]),axis=1)
                #合并
                data=pd.concat([result1,result2],axis=0)
                data=data.sort_values(by=['probability','predict_rank'],ascending=[True,True])
            else:#分数在分数线附近，但是没有上线人数，则不能用百分比预测
                rank2022=data[['predict_rank','predict_rank_std']]
                data['probability']=np.around(1-norm.cdf(rank,loc=rank2022['predict_rank'].values,scale=rank2022['predict_rank_std'].values),3)
                # data['probability']=rank2022.apply(lambda x:1-norm.cdf(rank, loc=x[0], scale=x[1]),axis=1)
                data=data.sort_values(by=['probability','predict_rank'],ascending=[True,True])
        else:#分数不在分数线附近，用排名预测      
            rank2022=data[['predict_rank','predict_rank_std']]
            data['probability']=np.around(1-norm.cdf(rank,loc=rank2022['predict_rank'].values,scale=rank2022['predict_rank_std'].values),3)
            # data['probability']=rank2022.apply(lambda x:1-norm.cdf(rank, loc=x[0], scale=x[1]),axis=1)
            data=data.sort_values(by=['probability','predict_rank'],ascending=[True,True])
    data=data.reset_index(drop=True)
    if not showall:
        data=data.drop(data[data['probability']<0.01].index)
        data=data.drop(data[np.isnan(data['probability'])].index)
    else:
        data['probability'][np.isnan(data['probability'])]=-1
    return data
    
if __name__ == '__main__':
    import time
    province=10
    # from GaoKao2021.solution import *
    # data=pickle.load(open(r'./GaoKao2021/DataResult/%s.pkl'%province,'rb'))
    data=pickle.load(open(r'./GaoKao2021/DataRaw/%s.pkl'%province,'rb'))
    # data=data[(data['college_id']==506)&(data['sg_name']=='208')]
    # data=data.loc[[3339]]
    t=time.time()
    result=probability_old_gaokao(data,score=532,rank=53078,province=10,wenli=2,showall=True)
    print(time.time()-t)
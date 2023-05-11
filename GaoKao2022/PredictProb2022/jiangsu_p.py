# -*- coding: utf-8 -*-
"""
Created on Sat May  8 15:25:09 2021

@author: Thinkpad
"""


import pandas as pd
import pickle
from scipy.stats import norm
import numpy as np
import time

import warnings
warnings.filterwarnings('ignore')

# import os
# os.chdir(r'C:\Users\Thinkpad\Desktop\xm\predict_score')

def probability_jiangsu(data,score,rank,province,wenli,showall=False):
    '''
    适用省份:江苏
    ID:10
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
    t=time.localtime()
    if t.tm_year>=2021&t.tm_mon>=6&t.tm_mday>=7:
        xian=[]
    else:
        xian=data[data['batch_score']!=-1]['batch_score'].unique()
    xian=xian[(score-xian<30)&(score-xian>=0)]
    if len(xian)==1 and data['batch_rank'].unique()[0]>0:#如果分数在分数线附近
        batch_renshu=data[data['batch_score']==xian[0]]#找到上线人数
        if len(batch_renshu)>0:
            #上线的院校用排名百分比预测
            rank_p=rank/batch_renshu['batch_rank'].values[0]#计算排名百分位
            result1=data[data['batch_text']==batch_renshu['batch_text'].values[0]]#将属于该线的院校提取出来
            rank_p2021=result1[['rank_p_2021','rank_p_2021_std']]
            result1['probability']=np.around(1-norm.cdf(rank_p,loc=rank_p2021['rank_p_2021'].values,scale=rank_p2021['rank_p_2021_std'].values),3)
            # result1['probability']=rank_p2021.apply(lambda x:1-norm.cdf(rank_p, loc=x[0], scale=x[1]),axis=1)
            #其它院校用排名预测
            result2=data[data['batch_text']!=batch_renshu['batch_text'].values[0]]
            rank2021=result2[['rank_2021','rank_2021_std']]
            result2['probability']=np.around(1-norm.cdf(rank,loc=rank2021['rank_2021'].values,scale=rank2021['rank_2021_std'].values),3)
            # result2['probability']=rank2021.apply(lambda x:1-norm.cdf(rank, loc=x[0], scale=x[1]),axis=1)
            #合并
            data=pd.concat([result1,result2],axis=0)
            data=data.sort_values(by=['probability','college_id'],ascending=[True,True])
        else:#分数在分数线附近，但是没有上线人数，则不能用百分比预测
            rank2021=data[['rank_2021','rank_2021_std']]
            data['probability']=np.around(1-norm.cdf(rank,loc=rank2021['rank_2021'].values,scale=rank2021['rank_2021_std'].values),3)
            # data['probability']=rank2021.apply(lambda x:1-norm.cdf(rank, loc=x[0], scale=x[1]),axis=1)
            data=data.sort_values(by=['probability','college_id'],ascending=[True,True])
    else:#分数不在分数线附近，用排名预测      
        rank2021=data[['rank_2021','rank_2021_std']]
        data['probability']=np.around(1-norm.cdf(rank,loc=rank2021['rank_2021'].values,scale=rank2021['rank_2021_std'].values),3)
        # data['probability']=rank2021.apply(lambda x:1-norm.cdf(rank, loc=x[0], scale=x[1]),axis=1)
        data=data.sort_values(by=['probability','college_id'],ascending=[True,True])
    if not showall:
        data=data.reset_index(drop=True)
        data=data.drop(data[data['probability']<0.01].index)
        data=data.drop(data[np.isnan(data['probability'])].index)
    return data
    
if __name__ == '__main__':
    import time
    province=10
    data=pickle.load(open(r'./GaoKao2021/DataRaw/%s.pkl'%province,'rb'))
    # data=data[4380:4381]
    t=time.time()
    result=probability_jiangsu(data,score=230,rank=60000,province=10,wenli=1,showall=False)
    print(time.time()-t)
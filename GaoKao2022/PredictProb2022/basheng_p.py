# -*- coding: utf-8 -*-
"""
Created on Thu May  6 12:17:51 2022

@author: Thinkpad
"""


import pandas as pd
import pickle
from scipy.stats import norm
import numpy as np
import time
# import os
# os.chdir(r'C:\Users\Thinkpad\Desktop\xm\predict_score')

def probability_basheng(data,score,rank,province,wenli,showall=False):
    '''
    计算八省录取概率
    Parameters
    ----------
    data:dataframe
        整个院校df表
    score:int
    rank:int
    province:int
    wenli:int
    showall:bool,optional
        是否展示所有结果。false会筛掉概率小于0.1%和没有数据的结果,true会返回所有结果。默认false
    
    Returns
    -------
    data:dataframe
        整个院校df表，增加2022年的预测录取概率
    '''
    xian=data[(data['wenli']==wenli)&(data['batch_score']!=-1)]['batch_score'].unique()
    xian=xian[(score-xian<30)&(score-xian>=0)]
    if len(xian)==1 and data['batch_rank'].unique()[0]>0:#如果分数在分数线附近
        batch_renshu=data[(data['wenli']==wenli)&(data['batch_score']==xian[0])]#找到上线人数
        if len(batch_renshu)>0:
            #上线的院校用排名百分比预测
            rank_p=rank/batch_renshu['batch_rank'].values[0]#计算排名百分位
            result1=data[(data['wenli']==wenli)&\
                         (data['batch_text']==batch_renshu['batch_text'].values[0])]#将属于该线的院校提取出来
            rank_p2022=result1[['predict_rank_p','predict_rank_p_std']]
            result1['probability']=np.around(1-norm.cdf(rank_p,loc=rank_p2022['predict_rank_p'].values,scale=rank_p2022['predict_rank_p_std'].values),3)
            #其它院校用排名预测
            result2=data[(data['wenli']==wenli)&\
                         (data['batch_text']!=batch_renshu['batch_text'].values[0])]
            rank2022=result2[['predict_rank','predict_rank_std']]
            result2['probability']=np.around(1-norm.cdf(rank,loc=rank2022['predict_rank'].values,scale=rank2022['predict_rank_std'].values),3)
            #合并
            data=pd.concat([result1,result2],axis=0)
            data=data.sort_values(by='probability',ascending=True)
        else:#分数在分数线附近，但是没有上线人数，则不能用百分比预测
            data=data[data['wenli']==wenli]
            rank2022=data[['predict_rank','predict_rank_std']]
            data['probability']=np.around(1-norm.cdf(rank,loc=rank2022['predict_rank'].values,scale=rank2022['predict_rank_std'].values),3)
            data=data.sort_values(by='probability',ascending=True)
    else:#分数不在分数线附近，用排名预测
        data=data[data['wenli']==wenli]
        rank2022=data[['predict_rank','predict_rank_std']]
        data['probability']=np.around(1-norm.cdf(rank,loc=rank2022['predict_rank'].values,scale=rank2022['predict_rank_std'].values),3)
        data=data.sort_values(by='probability',ascending=True)

    data=data.reset_index(drop=True)

    if not showall:
        data=data.drop(data[data['probability']<0.01].index)
        data=data.drop(data[np.isnan(data['probability'])].index)
    else:
        data['probability'][np.isnan(data['probability'])]=-1
    return data
    
if __name__ == '__main__':
    data=pickle.load(open(r'./resource/a_predict.pkl','rb'))
    result=probability_basheng(data,score=545,rank=28679,province=16,wenli=1)
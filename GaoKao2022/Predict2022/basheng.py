# -*- coding: utf-8 -*-
"""
Created on Thu May  6 10:47:26 2021

@author: Thinkpad
"""


import pickle
import pandas as pd
from sklearn import linear_model
import numpy as np

from tqdm import tqdm
tqdm.pandas(desc='pandas bar')

def predict_basheng(data):
    '''
    预测八省高考分数和排名
    年份一视同仁
    Parameters
    ----------
    data:一行df数据
        
    Returns
    -------
    data:dataframe
        整个院校df表，增加2022年的预测分数、排名和排名百分比
    '''
    x=[[2017],[2018],[2019],[2020],[2021]]
    #分数
    huber_score=linear_model.HuberRegressor()#分数回归模型
    minscore_y=data[['minscore_2017','minscore_2018','minscore_2019','minscore_2020','minscore_2021']].values
    x_=[x[i] for i in range(5) if minscore_y[i]!=-1]
    minscore_y=[minscore_y[i] for i in range(5) if minscore_y[i]!=-1]
    try:
        try:#先尝试huber模型
            huber_score.fit(x_,minscore_y)
        except Exception:#在梯度出现错误后，检测是否有足够的数据，若有换为RANSAC模型
            if len(minscore_y)>1:
                huber_score=linear_model.RANSACRegressor()
                huber_score.fit(x_,minscore_y)
        predict_minscore=huber_score.predict([[2022]])[0]
        #数据或模型异常时可能出现小于0的情况
        if predict_minscore<=0:
            predict_minscore=data['minscore_2021'].values
        #假设数据符合正态分布，且历年数据均处于99%概率的区间，则预测数据在区间外为小概率事件，纠正
        if predict_minscore<np.mean(minscore_y)-3*(max(minscore_y)-min(minscore_y))/4:
            predict_minscore=np.mean(minscore_y)-3*(max(minscore_y)-min(minscore_y))/4
        elif predict_minscore>np.mean(minscore_y)+3*(max(minscore_y)-min(minscore_y))/4:
            predict_minscore=np.mean(minscore_y)+3*(max(minscore_y)-min(minscore_y))/4
        #假设全部数据符合分布，且落在95%概率的区间，生成分布
        if type(predict_minscore)==np.ndarray:
            data['predict_minscore']=predict_minscore[0]
        else:
            data['predict_minscore']=predict_minscore
        if max(abs(minscore_y-predict_minscore))==0:
            data['predict_minscore_std']=0.1*data['predict_minscore']
        else:
            data['predict_minscore_std']=min(max(abs(minscore_y-predict_minscore))/2,0.2*data['predict_minscore'])
    except Exception:
        if len(minscore_y)>0:
            data['predict_minscore']=max(minscore_y)
        else:
            data['predict_minscore']=data['minscore_2021']
        data['predict_minscore_std']=0.1*data['predict_minscore']
    #排名
    huber_rank=linear_model.HuberRegressor()#排名回归模型
    rank_y=data[['minscore_rank_2017','minscore_rank_2018','minscore_rank_2019','minscore_rank_2020','minscore_rank_2021']].values
    batch_rank=data[['batch_rank_2017','batch_rank_2018','batch_rank_2019','batch_rank_2020','batch_rank_2021']].values
    x_=[x[i] for i in range(5) if rank_y[i]!=-1]
    batch_rank=[batch_rank[i] for i in range(5) if rank_y[i]!=-1]
    rank_y=[rank_y[i] for i in range(5) if rank_y[i]!=-1]
    try:
        try:
            huber_rank.fit(x_,rank_y)
        except Exception:
            if len(rank_y)>1:
                huber_rank=linear_model.RANSACRegressor()
                huber_rank.fit(x_,rank_y)
        predict_rank=huber_rank.predict([[2022]])[0]
        if predict_rank<=0:
            predict_rank=data['minscore_rank_2021'].values
        if predict_rank<np.mean(rank_y)-3*(max(rank_y)-min(rank_y))/4:
            predict_rank=np.mean(rank_y)-3*(max(rank_y)-min(rank_y))/4
        elif predict_rank>np.mean(rank_y)+3*(max(rank_y)-min(rank_y))/4:
            predict_rank=np.mean(rank_y)+3*(max(rank_y)-min(rank_y))/4
        if type(predict_rank)==np.ndarray:
            data['predict_rank']=predict_rank[0]
        else:
            data['predict_rank']=predict_rank
        if max(abs(rank_y-predict_rank))==0:
            data['predict_rank_std']=0.1*data['predict_rank']
        else:
            data['predict_rank_std']=max(min(max(abs(rank_y-predict_rank))/2,0.2*data['predict_rank']),0.01*data['predict_rank'])
    except Exception:
        if len(rank_y)>0:
            data['predict_rank']=max(rank_y)
        else:
            data['predict_rank']=data['minscore_rank_2020']
        data['predict_rank_std']=0.1*data['predict_rank']
    #排名百分比
    huber_rank_p=linear_model.HuberRegressor()#排名比例回归模型
    # rank_p_y=data[['minscore_percent_2017','minscore_percent_2018','minscore_percent_2019','minscore_percent_2020']].values
    rank_p_y=np.asarray(rank_y)/np.asarray(batch_rank)#计算排名百分位
    l=len(rank_p_y)
    if l>0:
        x_=[x[i] for i in range(l) if rank_p_y[i]>0.00001]#排除排名太前的
        rank_p_y=[rank_p_y[i] for i in range(l) if rank_p_y[i]>0.00001]
    else:
        x_=[]
    try:
        try:
            huber_rank_p.fit(x_,rank_p_y)
        except Exception:
            if len(rank_p_y)>1:
                huber_rank_p=linear_model.RANSACRegressor()
                huber_rank_p.fit(x_,rank_p_y)
        predict_rank_p=huber_rank_p.predict([[2022]])[0]
        if predict_rank_p<=0:
            predict_rank_p=np.float64(data['minscore_rank_2021']/data['batch_rank_2021'])
        if predict_rank_p<np.mean(rank_p_y)-3*(max(rank_p_y)-min(rank_p_y))/4:
            predict_rank_p=np.mean(rank_p_y)-3*(max(rank_p_y)-min(rank_p_y))/4
        elif predict_rank_p>np.mean(rank_p_y)+3*(max(rank_p_y)-min(rank_p_y))/4:
            predict_rank_p=np.mean(rank_p_y)+3*(max(rank_p_y)-min(rank_p_y))/4
        if type(predict_rank_p)==np.ndarray:
            data['predict_rank_p']=predict_rank_p[0]
        else:
            data['predict_rank_p']=predict_rank_p
        if max(abs(rank_p_y-predict_rank_p))==0:
            data['predict_rank_p_std']=0.1*data['predict_rank_p']
        else:
            data['predict_rank_p_std']=min(max(abs(rank_p_y-predict_rank_p))/2,0.2*data['predict_rank_p'])
    except Exception:
        if len(rank_p_y)>0:
            data['predict_rank_p']=max(rank_p_y)
        else:
            data['predict_rank_p']=-1
        data['predict_rank_p_std']=0.1*data['predict_rank_p']
    return data

if __name__ == '__main__':
    # data=pickle.load(open(r'./resource/a.pkl','rb'))
    # data=a[1:2]
    # data=data[1:10].apply(lambda x:predict_oldgaokao(x),axis=1)
    from GaoKao2021.MySQLBase.ProvinceNew import *
    from GaoKao2021.MySQLBase.ProvinceOld import *
    province_list = [11]
    for province in province_list:
        print(province)
        a = DataProvinceNewZy(province)
        a.data = a.data.progress_apply(lambda x: predict_basheng(x), axis=1)
        with open(r'../DataResult/%s.pkl' % province, 'wb') as f:
            pickle.dump(a, f)
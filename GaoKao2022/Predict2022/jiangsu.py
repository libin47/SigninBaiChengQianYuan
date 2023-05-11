# -*- coding: utf-8 -*-
"""
Created on Sat May  8 13:52:36 2021

@author: Thinkpad
"""


import pickle
import pandas as pd
from sklearn import linear_model
import numpy as np
from random import uniform

from tqdm import tqdm
tqdm.pandas(desc='pandas bar')

# import os
# os.chdir(r'C:\Users\Thinkpad\Desktop\xm\predict_score')



def predict_jiangsu(data):
    '''
    适用省份:江苏
    ID:10
    Parameters
    ----------
    data:一行df数据
        
    Returns
    -------
    data:dataframe
        整个院校df表，增加2021年的预测分数、排名和排名百分比
    '''
    x=[[2017],[2018],[2019],[2020]]
    #分数
    huber_score=linear_model.HuberRegressor()#排名回归模型
    minscore_y=data[['minscore_2017','minscore_2018','minscore_2019','minscore_2020']].values
    x_=[x[i] for i in range(4) if minscore_y[i]!=-1]
    minscore_y=[minscore_y[i] for i in range(4) if minscore_y[i]!=-1]
    try:
        try:#先尝试huber模型
            huber_score.fit(x_,minscore_y)
            # inliers=~huber_score.outliers_#记录异常值
        except Exception:#在梯度出现错误后，检测是否有足够的数据，若有换为RANSAC模型
            if len(minscore_y)>1:
                huber_score=linear_model.RANSACRegressor()
                huber_score.fit(x_,minscore_y)
                # inliers=huber_score.inlier_mask_#记录合理值
        # if len(minscore_y)>1:
            # minscore_y=[minscore_y[i] for i in np.where(inliers)[0]]
        minscore_2021=huber_score.predict([[2021]])[0]
        #数据或模型异常时可能出现小于0的情况
        if minscore_2021<=0:
            minscore_2021=data['minscore_2020'].values
        #假设数据符合正态分布，且历年数据均处于99%概率的区间，则预测数据在区间外为小概率事件，纠正
        if minscore_2021<np.mean(minscore_y)-3*(max(minscore_y)-min(minscore_y))/4:
            minscore_2021=np.mean(minscore_y)-3*(max(minscore_y)-min(minscore_y))/4
        elif minscore_2021>np.mean(minscore_y)+3*(max(minscore_y)-min(minscore_y))/4:
            minscore_2021=np.mean(minscore_y)+3*(max(minscore_y)-min(minscore_y))/4
        #假设全部数据符合分布，且落在95%概率的区间，生成分布
        if type(minscore_2021)==np.ndarray:
            data['minscore_2021']=minscore_2021[0]
        else:
            data['minscore_2021']=minscore_2021
        if max(abs(minscore_y-minscore_2021))==0:
            data['minscore_2021_std']=0.1*data['minscore_2021']
        else:
            data['minscore_2021_std']=min(max(abs(minscore_y-minscore_2021))/2,0.2*data['minscore_2021'])
    except Exception:#没有足够数据时用2020年数据填充
        if len(minscore_y)>0:#防止其它意外情况
            data['minscore_2021']=max(minscore_y)*uniform(0.98,1.02)
        else:#填充均值
            data['minscore_2021']=data['minscore_2020']*uniform(0.98,1.02)
        data['minscore_2021_std']=0.1*data['minscore_2021']#填充标准差
    #排名
    huber_rank=linear_model.HuberRegressor()#分数回归模型
    rank_y=data[['minscore_rank_2017','minscore_rank_2018','minscore_rank_2019','minscore_rank_2020']].values
    rank_y[rank_y==0]=-1
    x_=[x[i] for i in range(4) if rank_y[i]!=-1]
    rank_y=[rank_y[i] for i in range(4) if rank_y[i]!=-1]
    try:
        try:
            huber_rank.fit(x_,rank_y)
            # inliers=~huber_rank.outliers_#记录异常值
        except Exception:
            if len(rank_y)>1:
                huber_rank=linear_model.RANSACRegressor()
                huber_rank.fit(x_,rank_y)
                # inliers=huber_rank.inlier_mask_#记录合理值
        # if len(rank_y)>1:
            # rank_y=[rank_y[i] for i in np.where(inliers)[0]]
        rank_2021=huber_rank.predict([[2021]])[0]
        if rank_2021<=0:
            rank_2021=data['minscore_rank_2020'].values
        if rank_2021<np.mean(rank_y)-3*(max(rank_y)-min(rank_y))/4:
            rank_2021=np.mean(rank_y)-3*(max(rank_y)-min(rank_y))/4
        elif rank_2021>np.mean(rank_y)+3*(max(rank_y)-min(rank_y))/4:
            rank_2021=np.mean(rank_y)+3*(max(rank_y)-min(rank_y))/4
        if type(rank_2021)==np.ndarray:
            data['rank_2021']=rank_2021[0]
        else:
            data['rank_2021']=rank_2021
        if max(abs(rank_y-rank_2021))==0:
            data['rank_2021_std']=0.1*data['rank_2021']
        else:
            data['rank_2021_std']=min(max(abs(rank_y-rank_2021))/2,0.2*data['rank_2021'])
    except Exception:
        if len(rank_y)>0:
            data['rank_2021']=max(rank_y)*uniform(0.98,1.02)
        else:
            data['rank_2021']=data['minscore_rank_2020']*uniform(0.98,1.02)
        data['rank_2021_std']=0.1*data['rank_2021']
    #排名百分比
    huber_rank_p=linear_model.HuberRegressor()#排名比例回归模型
    rank_p_y=data[['minscore_percent_2017','minscore_percent_2018','minscore_percent_2019','minscore_percent_2020']].values
    x_=[x[i] for i in range(4) if rank_p_y[i]>0.00001]
    rank_p_y=[rank_p_y[i] for i in range(4) if rank_p_y[i]>0.00001]
    try:
        try:
            huber_rank_p.fit(x_,rank_p_y)
            # inliers=~huber_rank_p.outliers_#记录异常值
        except Exception:
            if len(rank_p_y)>1:
                huber_rank_p=linear_model.RANSACRegressor()
                huber_rank_p.fit(x_,rank_p_y)
                # inliers=huber_rank_p.inlier_mask_#记录合理值
        # if len(rank_p_y)>1:
            # rank_p_y=[rank_p_y[i] for i in np.where(inliers)[0]]
        rank_p_2021=huber_rank_p.predict([[2021]])[0]
        if rank_p_2021<=0:
            rank_p_2021=data['minscore_rank_2020'].values
        if rank_p_2021<np.mean(rank_p_y)-3*(max(rank_p_y)-min(rank_p_y))/4:
            rank_p_2021=np.mean(rank_p_y)-3*(max(rank_p_y)-min(rank_p_y))/4
        elif rank_p_2021>np.mean(rank_p_y)+3*(max(rank_p_y)-min(rank_p_y))/4:
            rank_p_2021=np.mean(rank_p_y)+3*(max(rank_p_y)-min(rank_p_y))/4
        if type(rank_p_2021)==np.ndarray:
            data['rank_p_2021']=rank_p_2021[0]
        else:
            data['rank_p_2021']=rank_p_2021
        if max(abs(rank_p_y-rank_p_2021))==0:
            data['rank_p_2021_std']=0.1*data['rank_p_2021']
        else:
            data['rank_p_2021_std']=min(max(abs(rank_p_y-rank_p_2021))/2,0.2*data['rank_p_2021'])
    except Exception:
        if len(rank_p_y)>0:
            data['rank_p_2021']=max(rank_p_y)*uniform(0.98,1.02)
        else:
            data['rank_p_2021']=data['minscore_percent_2020']*uniform(0.98,1.02)
        data['rank_p_2021_std']=0.1*data['rank_p_2021']
    return data

if __name__ == '__main__':
    # province=10
    # data=pickle.load(open(r'./GaoKao2021/DataRaw/%s.pkl'%province,'rb'))
    # data=data.reset_index(drop=True)
    # data=data[(data['college_id']==24)]
    # data=data.loc[[20]]
    # data=data.progress_apply(lambda x:pbredict_oldgaokao(x),axis=1)
    # with open(r'./GaoKao2021/DataRaw/%s.pkl'%province,'wb') as f:
    #     pickle.dump(data,f)
    
    # from GaoKao2021.MySQLBase.ProvinceOld import *
    from GaoKao2021.MySQLBase.Province8New import *
    # from GaoKao2021.MySQLBase.ProvinceNew import *
    province=10
    a = DataProvince8New(province)
    data = a.data.progress_apply(lambda x: predict_jiangsu(x), axis=1)
    with open(r'./GaoKao2021/DataRaw/%s.pkl'%province,'wb') as f:
        pickle.dump(data,f)
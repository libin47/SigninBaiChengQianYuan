# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 11:45:23 2022

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



def predict_oldgaokao(data):
    '''
    21年优先
    适用省份:河北,山西,内蒙古,辽宁,吉林,黑龙江,上海,浙江,安徽,福建,江西,河南,湖北,湖南,广东,广西,甘肃,陕西,新疆,青海,宁夏,重庆,四川,贵州,云南,西藏
    ID:3,4,5,6,7,8,9,11,12,13,14,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31
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
    huber_score=linear_model.HuberRegressor()#排名回归模型
    minscore_y=data[['minscore_2017','minscore_2018','minscore_2019','minscore_2020','minscore_2021']].values
    x_=[x[i] for i in range(5) if minscore_y[i]!=-1]
    minscore_y=[minscore_y[i] for i in range(5) if minscore_y[i]!=-1]
    try:
        try:#先尝试huber模型
            huber_score.fit(x_,minscore_y)
            outliers=huber_score.outliers_#记录异常值
        except Exception:#在梯度出现错误后，检测是否有足够的数据，若有换为RANSAC模型
            if len(minscore_y)>1:
                huber_score=linear_model.RANSACRegressor()
                huber_score.fit(x_,minscore_y)
                outliers=~huber_score.inlier_mask_#记录合理值
        # if len(minscore_y)>1:
            # minscore_y=[minscore_y[i] for i in np.where(inliers)[0]]
        predict_minscore=huber_score.predict([[2022]])[0]
        out_21=0#20年是否异常值的标记
        if [2021] in np.array(x_)[outliers].tolist():#判断21年是否异常值
            out_21=1
        if out_21:#如果21年是异常值，以21年为准，非异常年份计算分布的标准差
            predict_minscore=minscore_y[-1]*uniform(0.98,1.02)
            minscore_y_=[minscore_y[i] for i in range(5) if ~outliers[i]]
            predict_minscore_std=abs(max(minscore_y_)-np.mean(minscore_y_))/2
            data['predict_minscore']=predict_minscore
            data['predict_minscore_std']=max(min(predict_minscore_std,0.2*data['predict_minscore']),0.01*data['predict_minscore'])
        else:
            #数据或模型异常时可能出现小于0的情况
            if predict_minscore<=0:
                predict_minscore=np.float64(data['minscore_2021'])
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
    except Exception:#没有足够数据时用2021年数据填充
        if data['minscore_2021']>0:#防止其它意外情况
            data['predict_minscore']=data['minscore_2021']*uniform(0.98,1.02)
        else:#填充均值
            data['predict_minscore']=-1
        data['predict_minscore_std']=0.1*data['predict_minscore']#填充标准差
    #排名
    huber_rank=linear_model.HuberRegressor()#分数回归模型
    rank_y=data[['minscore_rank_2017','minscore_rank_2018','minscore_rank_2019','minscore_rank_2020','minscore_rank_2021']].values
    batch_rank=data[['batch_rank_2017','batch_rank_2018','batch_rank_2019','batch_rank_2020','batch_rank_2021']].values
    rank_y[rank_y==0]=-1
    x_=[x[i] for i in range(5) if rank_y[i]!=-1]
    batch_rank=[batch_rank[i] for i in range(5) if rank_y[i]!=-1]
    rank_y=[rank_y[i] for i in range(5) if rank_y[i]!=-1]
    try:
        try:
            huber_rank.fit(x_,rank_y)
            outliers=huber_rank.outliers_#记录异常值
        except Exception:
            if len(rank_y)>1:
                huber_rank=linear_model.RANSACRegressor()
                huber_rank.fit(x_,rank_y)
                outliers=~huber_rank.inlier_mask_#记录合理值
        # if len(rank_y)>1:
            # rank_y=[rank_y[i] for i in np.where(inliers)[0]]
        predict_rank=huber_rank.predict([[2022]])[0]
        out_21=0#21年是否异常值的标记
        if [2021] in np.array(x_)[outliers].tolist():#判断21年是否异常值
            out_21=1
        if out_21:#如果21年是异常值，以21年为准，非异常年份计算分布的标准差
            predict_rank=rank_y[-1]*uniform(0.98,1.02)
            rank_y_=[rank_y[i] for i in range(5) if ~outliers[i]]
            predict_rank_std=abs(max(rank_y_)-np.mean(rank_y_))/2
            data['predict_rank']=predict_rank
            data['predict_rank_std']=max(min(predict_rank_std,0.2*data['predict_rank']),0.01*data['predict_rank'])
        else:#否则正常计算
            if predict_rank<=0:
                predict_rank=np.float64(data['minscore_rank_2021'])
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
        if data['minscore_rank_2021']>0:
            data['predict_rank']=data['minscore_rank_2021']*uniform(0.98,1.02)
        else:
            data['predict_rank']=-1
        data['predict_rank_std']=0.1*data['predict_rank']
    #排名百分比
    huber_rank_p=linear_model.HuberRegressor()#排名比例回归模型
    # 字段没了，在处理排名时同时筛选批次线
    # rank_p_y=data[['minscore_percent_2017','minscore_percent_2018','minscore_percent_2019','minscore_percent_2020','minscore_percent_2021']].values
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
            outliers=huber_rank_p.outliers_#记录异常值
        except Exception:
            if len(rank_p_y)>1:
                huber_rank_p=linear_model.RANSACRegressor()
                huber_rank_p.fit(x_,rank_p_y)
                outliers=~huber_rank_p.inlier_mask_#记录合理值
        # if len(rank_p_y)>1:
            # rank_p_y=[rank_p_y[i] for i in np.where(inliers)[0]]
        predict_rank_p=huber_rank_p.predict([[2022]])[0]
        out_21=0#21年是否异常值的标记
        if [2021] in np.array(x_)[outliers].tolist():#判断21年是否异常值
            out_21=1
        if out_21:#如果21年是异常值，以21年为准，非异常年份计算分布的标准差
            predict_rank_p=rank_p_y[-1]*uniform(0.98,1.02)
            rank_p_y_=[rank_p_y[i] for i in range(5) if ~outliers[i]]
            predict_rank_p_std=abs(max(rank_p_y_)-np.mean(rank_p_y_))/2
            data['predict_rank_p']=predict_rank_p
            data['predict_rank_p_std']=min(predict_rank_p_std,0.2*data['predict_rank_p'])
        else:
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
        if data['minscore_rank_2021']/data['batch_rank_2021']>0:
            data['predict_rank_p']=data['minscore_rank_2021']/data['batch_rank_2021']*uniform(0.98,1.02)
        else:
            data['predict_rank_p']=-1
        data['predict_rank_p_std']=0.1*data['predict_rank_p']
    return data

if __name__ == '__main__':
    province=10
    data=pickle.load(open(r'./GaoKao2021/DataRaw/%s.pkl'%province,'rb'))
    data=data[(data['college_id']==120)]
    data=data.loc[[10677]]
    # data=data.progress_apply(lambda x:predict_oldgaokao(x),axis=1)
    # with open(r'./GaoKao2021/DataRaw/%s.pkl'%province,'wb') as f:
    #     pickle.dump(data,f)
    
    # a=data[['college_id','schoolname','rank_2021','minscore_rank_2021','minscore_rank_2019_wen',\
    #             'minscore_rank_2019_li','minscore_rank_2018_wen','minscore_rank_2018_li','minscore_rank_2017_wen',\
    #             'minscore_rank_2017_li']]
    
    # from GaoKao2021.MySQLBase.ProvinceOld import *
    # from GaoKao2021.MySQLBase.Province8New import *
    # from GaoKao2021.MySQLBase.ProvinceNew import *
    # province=13
    # # a = DataProvinceOld(province,source='youzy')
    # a = DataProvince8New(province)
    # a = DataProvinceNewZy(province,source='youzy')
    # data = a.data.progress_apply(lambda x: predict_oldgaokao(x), axis=1)
    # with open(r'./GaoKao2021/DataRaw/%s.pkl'%province,'wb') as f:
    #     pickle.dump(data,f)
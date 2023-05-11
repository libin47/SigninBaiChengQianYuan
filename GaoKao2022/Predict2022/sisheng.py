# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 14:54:50 2021

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



def predict_sisheng(data):
    '''
    预测四省高考分数和排名
    Parameters
    ----------
    data:一行df数据
        
    Returns
    -------
    data:dataframe
        整个院校df表，增加2021年的预测分数、排名和排名百分比
    '''
    x=[[2017],[2018],[2019]]
    x2=[[2019],[2020],[2021]]
    #分数
    huber_score=linear_model.HuberRegressor()#排名回归模型
    minscore_y=data[['minscore_2017_wen','minscore_2017_li','minscore_2018_wen','minscore_2018_li',\
                     'minscore_2019_wen','minscore_2019_li']].values
    minscore_y_=[max(minscore_y[0:2]),max(minscore_y[2:4]),max(minscore_y[4:6])]
    x_=[x[i] for i in range(3) if minscore_y_[i]!=-1]
    minscore_y_=[minscore_y_[i] for i in range(3) if minscore_y_[i]!=-1]
    try:
        try:#先尝试huber模型
            huber_score.fit(x_,minscore_y_)
            # inliers=~huber_score.outliers_#记录异常值
        except Exception:#在梯度出现错误后，检测是否有足够的数据，若有换为RANSAC模型
            if len(minscore_y_)>1:
                huber_score=linear_model.RANSACRegressor()
                huber_score.fit(x_,minscore_y_)
                # inliers=huber_score.inlier_mask_#记录合理值
        # if len(minscore_y_)>1:
            # minscore_y_=[minscore_y_[i] for i in np.where(inliers)[0]]
        minscore_2020=huber_score.predict([[2020]])[0]#按模型预测20年成绩
        #数据或模型异常时可能出现小于0的情况
        if minscore_2020<=0:
            minscore_2020=max(data[['minscore_2019_wen','minscore_2019_li']].values)
        #假设数据符合正态分布，且历年数据均处于99%概率的区间，则预测数据在区间外为小概率事件，纠正
        if minscore_2020<np.mean(minscore_y_)-3*(max(minscore_y_)-min(minscore_y_))/4:
            minscore_2020=np.mean(minscore_y_)-3*(max(minscore_y_)-min(minscore_y_))/4
        elif minscore_2020>np.mean(minscore_y_)+3*(max(minscore_y_)-min(minscore_y_))/4:
            minscore_2020=np.mean(minscore_y_)+3*(max(minscore_y_)-min(minscore_y_))/4
        fac=data['minscore_2020']/minscore_2020
        if type(fac)==np.ndarray:
            fac=fac[0]
        if fac<0:
            fac=1
        #用前三年的数据预测2019年，与后两年组成三年的数据再来一次预测
        huber_score=linear_model.HuberRegressor()
        minscore_2019=huber_score.predict([[2019]])[0]*fac#用预测预测19年在新高考的情况下的分数线，增加数据量
        minscore_new_y=[minscore_2019,data['minscore_2020'],data['minscore_2021']]
        x_=[x2[i] for i in range(3) if minscore_new_y[i]>1]
        minscore_new_y=[minscore_new_y[i] for i in range(3) if minscore_new_y[i]>1]
        try:#先尝试huber模型
            huber_score.fit(x_,minscore_new_y)
        except Exception:#在梯度出现错误后，检测是否有足够的数据，若有换为RANSAC模型
            if len(minscore_new_y)>1:
                huber_score=linear_model.RANSACRegressor()
                huber_score.fit(x_,minscore_new_y)
        predict_minscore=huber_score.predict([[2022]])[0]#按模型预测20年成绩
        #数据或模型异常时可能出现小于0的情况
        if predict_minscore<=0:
            predict_minscore=data['minscore_2021'].values
        #假设数据符合正态分布，且历年数据均处于99%概率的区间，则预测数据在区间外为小概率事件，纠正
        if predict_minscore<np.mean(minscore_new_y)-3*(max(minscore_new_y)-min(minscore_new_y))/4:
            predict_minscore=np.mean(minscore_new_y)-3*(max(minscore_new_y)-min(minscore_new_y))/4
        elif predict_minscore>np.mean(minscore_new_y)+3*(max(minscore_new_y)-min(minscore_new_y))/4:
            predict_minscore=np.mean(minscore_new_y)+3*(max(minscore_new_y)-min(minscore_new_y))/4
        #假设全部数据符合分布，且落在95%概率的区间，生成分布
        predict_minscore_std=max(abs(minscore_new_y-predict_minscore))/2
        if type(predict_minscore)==np.ndarray:
            data['predict_minscore']=predict_minscore[0]
        else:
            data['predict_minscore']=predict_minscore
        data['predict_minscore_std']=min(predict_minscore_std,0.2*data['predict_minscore'])
    except Exception:
        if data['minscore_2021']>0:
            data['predict_minscore']=data['minscore_2021']*uniform(0.98,1.02)
        elif data['minscore_2020']>0:
            data['predict_minscore']=data['minscore_2020']*uniform(0.98,1.02)
        elif len(minscore_y_)>0:
            data['predict_minscore']=max(minscore_y_)*uniform(0.98,1.02)
        else:
            data['predict_minscore']=-1
        data['predict_minscore_std']=0.1*data['predict_minscore']
    #排名
    huber_rank=linear_model.HuberRegressor()#分数回归模型
    rank_y=data[['minscore_rank_2017_wen','minscore_rank_2017_li','minscore_rank_2018_wen',\
                 'minscore_rank_2018_li','minscore_rank_2019_wen','minscore_rank_2019_li']].values
    rank_y[rank_y==0]=-1
    rank_y_=[sum(rank_y[0:2],1),sum(rank_y[2:4],1),sum(rank_y[4:6],1)]
    x_=[x[i] for i in range(3) if rank_y_[i]!=-1]
    rank_y_=[rank_y_[i] for i in range(3) if rank_y_[i]!=-1]
    try:
        try:
            huber_rank.fit(x_,rank_y_)
            # inliers=~huber_rank.outliers_
        except Exception:
            if len(rank_y_)>1:
                huber_rank=linear_model.RANSACRegressor()
                huber_rank.fit(x_,rank_y_)
                # inliers=huber_rank.inlier_mask_
        # if len(rank_y_)>1:
            # rank_y_=[rank_y_[i] for i in np.where(inliers)[0]]
        rank_2020=huber_rank.predict([[2020]])[0]
        if rank_2020<=0:
            rank_2020=max(data[['minscore_rank_2019_wen','minscore_rank_2019_li']].values)
        if rank_2020<np.mean(rank_y_)-3*(max(rank_y_)-min(rank_y_))/4:
            rank_2020=np.mean(rank_y_)-3*(max(rank_y_)-min(rank_y_))/4
        elif rank_2020>np.mean(rank_y_)+3*(max(rank_y_)-min(rank_y_))/4:
            rank_2020=np.mean(rank_y_)+3*(max(rank_y_)-min(rank_y_))/4
        fac=data['minscore_rank_2020']/rank_2020
        if type(fac)==np.ndarray:
            fac=fac[0]
        if fac<0:
            fac=1
        rank_2019=huber_rank.predict([[2019]])[0]*fac
        #再次预测
        huber_rank=linear_model.HuberRegressor()
        rank_new_y=[rank_2019,data['minscore_rank_2020'],data['minscore_rank_2021']]
        x_=[x2[i] for i in range(3) if rank_new_y[i]>1]
        rank_new_y=[rank_new_y[i] for i in range(3) if rank_new_y[i]>1]
        try:
            huber_rank.fit(x_,rank_new_y)
            # inliers=~huber_rank.outliers_
        except Exception:
            if len(rank_new_y)>1:
                huber_rank=linear_model.RANSACRegressor()
                huber_rank.fit(x_,rank_new_y)
                # inliers=huber_rank.inlier_mask_
        # if len(rank_y_)>1:
            # rank_y_=[rank_y_[i] for i in np.where(inliers)[0]]
        predict_rank=huber_rank.predict([[2022]])[0]
        if predict_rank<=0:
            predict_rank=data['minscore_rank_2021']
        if predict_rank<np.mean(rank_new_y)-3*(max(rank_new_y)-min(rank_new_y))/4:
            predict_rank=np.mean(rank_new_y)-3*(max(rank_new_y)-min(rank_new_y))/4
        elif predict_rank>np.mean(rank_new_y)+3*(max(rank_new_y)-min(rank_new_y))/4:
            predict_rank=np.mean(rank_new_y)+3*(max(rank_new_y)-min(rank_new_y))/4
        predict_rank_std=max(abs(rank_new_y-predict_rank))/2
        if type(predict_rank)==np.ndarray:
            data['predict_rank']=predict_rank[0]
        else:
            data['predict_rank']=predict_rank
        data['predict_rank_std']=max(min(predict_rank_std,0.2*data['predict_rank']),0.01*data['predict_rank'])
    except Exception:
        if data['minscore_rank_2021']>0:#以21年排名为准
            data['predict_rank']=data['minscore_rank_2021']*uniform(0.98,1.02)
        elif data['minscore_rank_2020']>0:
            data['predict_rank']=data['minscore_rank_2020']*uniform(0.98,1.02)
        elif len(rank_y_)>0:
            data['predict_rank']=max(rank_y_)*uniform(0.98,1.02)
        else:
            data['predict_rank']=-1
        data['predict_rank_std']=0.1*data['predict_rank']
    #排名百分比
    huber_rank_p=linear_model.HuberRegressor()#排名比例回归模型
    
    #计算排名百分比。+2可以让两个数据都缺失的时候的到0，从而排除缺失数据
    rank_p_y_=[sum(data[['minscore_rank_2017_wen','minscore_rank_2017_li']].values,2)/sum(data[['batch_rank_2017_wen','batch_rank_2017_li']].values,3),\
             sum(data[['minscore_rank_2018_wen','minscore_rank_2018_li']].values,2)/sum(data[['batch_rank_2018_wen','batch_rank_2018_li']].values,3),\
             sum(data[['minscore_rank_2019_wen','minscore_rank_2019_li']].values,2)/sum(data[['batch_rank_2019_wen','batch_rank_2019_li']].values,3)]  
    x_=[x[i] for i in range(3) if (rank_p_y_[i]>0.00001)&(rank_p_y_[i]!=2/3)]
    rank_p_y_=[rank_p_y_[i] for i in range(3) if (rank_p_y_[i]>0.00001)&(rank_p_y_[i]!=2/3)]
    data_suf_2020=1#判断2020数据是否齐全
    if any([data['minscore_rank_2020']<0,data['batch_rank_2020']<0]):
        data_suf_2020=-1
    data_suf_2021 = 1#判断2021数据是否齐全
    if any([data['minscore_rank_2021'] < 0, data['batch_rank_2021'] < 0]):
        data_suf_2021 = -1
    try:
        try:
            huber_rank_p.fit(x_,rank_p_y_)
            # inliers=~huber_rank_p.outliers_
        except Exception:
            if len(rank_p_y_)>1:
                huber_rank_p=linear_model.RANSACRegressor()
                huber_rank_p.fit(x_,rank_p_y_)
                # inliers=huber_rank_p.inlier_mask_
        # if len(rank_p_y_)>1:
            # rank_p_y_=[rank_p_y_[i] for i in np.where(inliers)[0]]
        rank_p_2020=huber_rank_p.predict([[2020]])[0]
        if rank_p_2020<=0:
            rank_p_2020=rank_p_y_[2]
        if rank_p_2020<np.mean(rank_p_y_)-3*(max(rank_p_y_)-min(rank_p_y_))/4:
            rank_p_2020=np.mean(rank_p_y_)-3*(max(rank_p_y_)-min(rank_p_y_))/4
        elif rank_p_2020>np.mean(rank_p_y_)+3*(max(rank_p_y_)-min(rank_p_y_))/4:
            rank_p_2020=np.mean(rank_p_y_)+3*(max(rank_p_y_)-min(rank_p_y_))/4
        fac=data_suf_2020*abs(data['minscore_rank_2020']/data['batch_rank_2020'])/rank_p_2020
        if type(fac)==np.ndarray:
            fac=fac[0]
        if fac<0:
            fac=1
        rank_p_2019=huber_rank_p.predict([[2019]])[0]*fac
        #再次预测
        huber_rank_p=linear_model.HuberRegressor()
        rank_new_p_y=[rank_p_2019,data_suf_2020*abs(data['minscore_rank_2020']/data['batch_rank_2020']),data_suf_2021*abs(data['minscore_rank_2021']/data['batch_rank_2021'])]#符号由数据是否充足决定
        x_=[x2[i] for i in range(3) if rank_new_p_y[i]>0.00001]
        rank_new_p_y=[rank_new_p_y[i] for i in range(3) if rank_new_p_y[i]>0.00001]   
        try:
            huber_rank_p.fit(x_,rank_new_p_y)
            # inliers=~huber_rank_p.outliers_
        except Exception:
            if len(rank_new_p_y)>1:
                huber_rank_p=linear_model.RANSACRegressor()
                huber_rank_p.fit(x_,rank_new_p_y)
                # inliers=huber_rank_p.inlier_mask_
        # if len(rank_p_y_)>1:
            # rank_p_y_=[rank_p_y_[i] for i in np.where(inliers)[0]]
        predict_rank_p=huber_rank_p.predict([[2022]])[0]
        if predict_rank_p<=0:
            predict_rank_p=rank_new_p_y[2]
        if predict_rank_p<np.mean(rank_new_p_y)-3*(max(rank_new_p_y)-min(rank_new_p_y))/4:
            predict_rank_p=np.mean(rank_new_p_y)-3*(max(rank_new_p_y)-min(rank_new_p_y))/4
        elif predict_rank_p>np.mean(rank_new_p_y)+3*(max(rank_new_p_y)-min(rank_new_p_y))/4:
            predict_rank_p=np.mean(rank_new_p_y)+3*(max(rank_new_p_y)-min(rank_new_p_y))/4
        predict_rank_p_std=max(abs(rank_new_p_y-predict_rank_p))/2
        if type(predict_rank_p)==np.ndarray:
            data['predict_rank_p']=predict_rank_p[0]
        else:
            data['predict_rank_p']=predict_rank_p
        data['predict_rank_p_std']=min(predict_rank_p_std,0.2*data['predict_rank_p'])
    except Exception:
        if data_suf_2021*abs(data['minscore_rank_2021']/data['batch_rank_2021'])>0:
            data['predict_rank_p']=data['minscore_rank_2021']/data['batch_rank_2021']*uniform(0.98,1.02)
        elif data_suf_2020*abs(data['minscore_rank_2020']/data['batch_rank_2020'])>0:
            data['predict_rank_p']=data['minscore_rank_2020']/data['batch_rank_2020']*uniform(0.98,1.02)
        elif len(rank_p_y_)>0:
            data['predict_rank_p']=max(rank_p_y_)*uniform(0.98,1.02)
        else:
            data['predict_rank_p']=-1
        data['predict_rank_p_std']=0.1*data['predict_rank_p']
    return data

if __name__ == '__main__':
    data=pickle.load(open(r'./GaoKao2021/DataRaw/2.pkl','rb'))
    data=data[data['college_id']==396]
    data=data.loc[[349]]
    data=data.progress_apply(lambda x:predict_sisheng(x),axis=1)
    with open(r'./GaoKao2021/DataRaw/1.pkl','wb') as f:
        pickle.dump(data,f)
    
    # a=data[['college_id','schoolname','rank_2021','minscore_rank_2020','minscore_rank_2019_wen',\
    #            'minscore_rank_2019_li','minscore_rank_2018_wen','minscore_rank_2018_li','minscore_rank_2017_wen',\
    #            'minscore_rank_2017_li']]
        
    # from GaoKao2021.MySQLBase.ProvinceNew import *
    # province=2
    # a = DataProvinceNewZy(province)
    # data = a.data.progress_apply(lambda x: predict_sisheng(x), axis=1)
    # with open(r'./GaoKao2021/DataRaw/%s.pkl'%province,'wb') as f:
    #     pickle.dump(data,f)
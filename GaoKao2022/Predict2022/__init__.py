# -*- coding: utf-8 -*-
from .basheng import predict_basheng
from .jiangsu import predict_jiangsu
from .oldgaokao import predict_oldgaokao
from .sisheng import predict_sisheng

from tqdm import tqdm
import numpy as np
tqdm.pandas(desc='pandas bar')


def predict_new(df, cfg):
    needs=['minscore_2017','minscore_2018','minscore_2019','minscore_2020','minscore_2021',\
          'minscore_rank_2017','minscore_rank_2018','minscore_rank_2019','minscore_rank_2020',\
          'minscore_rank_2021','batch_rank_2017','batch_rank_2018','batch_rank_2019',\
          'batch_rank_2020','batch_rank_2021']
    for need in needs:
        if need not in df.columns:
            df[need]=-1

    # quick test
    # for cl in ['predict_minscore', 'predict_minscore_std', 'predict_rank', 'predict_rank_std', 'predict_rank_p', 'predict_rank_p_std']:
    #     df[cl] = -1
    # return df

    if cfg['province_id'] in [3, 6, 10, 13, 17, 18, 19, 26]:
        df = df.progress_apply(lambda x: predict_basheng(x), axis=1)
    elif cfg['province_id'] == 10:
        df = df.progress_apply(lambda x: predict_jiangsu(x), axis=1)
    elif cfg['province_id'] in [1,2,15,20]:
        needs_sp=['minscore_2017_wen','minscore_2017_li','minscore_2018_wen','minscore_2018_li',\
                 'minscore_2019_wen','minscore_2019_li','minscore_rank_2017_wen',\
                 'minscore_rank_2017_li','minscore_rank_2018_wen','minscore_rank_2018_li',\
                 'minscore_rank_2019_wen','minscore_rank_2019_li','batch_rank_2017_wen',\
                 'batch_rank_2017_li','batch_rank_2018_wen','batch_rank_2018_li','batch_rank_2019_wen',\
                 'batch_rank_2019_li']
        for need_sp in needs_sp:
            if need_sp not in df.columns:
                df[need_sp]=-1
        df = df.progress_apply(lambda x: predict_sisheng(x), axis=1)
    else:
        df = df.progress_apply(lambda x: predict_oldgaokao(x), axis=1)

    # 合作院校手动调整
    if cfg['province_id']==19:
        try:
            df['predict_rank'] = df.apply(lambda x:
                                          x['predict_rank'] - 9999 if (x['province_id']==19) and (x['college_id'] in [1257]) and (x['predict_rank']>0)
                                          else x['predict_rank'], axis=1)

            # 碧桂园
            maxrank_22 = max(df[(df.college_id == 2296) & (df.wenli == 22) & (df.predict_rank > 0)]['predict_rank'])
            df['predict_rank_std'] = df.apply(lambda x:
                                          39216 if (x['college_id'] == 2296) and (x['predict_rank'] == maxrank_22) and (x['wenli'] == 22)
                                          else x['predict_rank_std'], axis=1)
            df['predict_rank'] = df.apply(lambda x:
                                          380784 if (x['college_id'] == 2296) and (x['predict_rank'] == maxrank_22) and (x['wenli'] == 22)
                                          else x['predict_rank'], axis=1)
            maxrank_21 = max(df[(df.college_id == 2296) & (df.wenli == 21) & (df.predict_rank > 0)]['predict_rank'])
            df['predict_rank_std'] = df.apply(lambda x:
                                          39216 if (x['college_id'] == 2296) and (x['predict_rank'] == maxrank_21) and (x['wenli'] == 21)
                                          else x['predict_rank_std'], axis=1)
            df['predict_rank'] = df.apply(lambda x:
                                          300784 if (x['college_id'] == 2296) and (x['predict_rank'] == maxrank_21) and (x['wenli'] == 21)
                                          else x['predict_rank'], axis=1)
        except:
            print("error: 特殊处理某些学校时")

    return df

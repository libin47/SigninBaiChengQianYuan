# -*- coding: utf-8 -*-
import numpy as np

from .basheng_p import probability_basheng
from .jiangsu_p import probability_jiangsu
from .oldgaokao_p import probability_old_gaokao
from .sisheng_p import probability_sisheng


def probability(df, province_id, wenli, score, rank, cengci=1):
    df = probability_old_gaokao(df, score, rank, province_id, wenli, cengci, showall=True)
    df['probability'] = np.round(df['probability'], 2)
    df['probability'][(df['probability']<0.01)&(df['probability']>-1)] = 0.01
    df['probability'][df['probability']>0.99] = 0.99
    return df



    if province_id in [3, 6, 10, 13, 17, 18, 19, 26]:
        df = probability_basheng(df, score,rank,province_id, wenli, showall=True)
    elif province_id in [1, 2, 15, 20]:
        df = probability_sisheng(df, score,rank,province_id, showall=True)
    elif province_id == 10:
        df = probability_jiangsu(df, score,rank,province_id, wenli, showall=True)
    else:
        df = probability_old_gaokao(df, score, rank, province_id, wenli, showall=True)
    return df
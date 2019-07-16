# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: entropy.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and Communications Technology
#==================================================================================

import numpy as np
from os import path


def calculate_entropy(eig_1, eig_2, eig_3):
    """
    オンライン学習2　SAR画像解析応用編
    
    固有値からエントロピーを計算します
    :param eig_1: 固有値行列1
    :param eig_2: 固有値行列2
    :param eig_3: 固有値行列3
    :return: エントロピー
    """
    
    p1 = eig_1 / (eig_1 + eig_2 + eig_3)
    p2 = eig_2 / (eig_1 + eig_2 + eig_3)
    p3 = eig_3 / (eig_1 + eig_2 + eig_3)
    
    #ここでゼロを代入するとlog0になってしまう
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0.1)(p1)
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0.1)(p2)
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0.1)(p3)

    print(p1.shape)

    #h = np.zeros(shape=p1, dtype=np.float32)
    #h = np.zeros_like(p1)
    h = -p1*(np.log(p1)/np.log(3))-p2*(np.log(p2)/np.log(3))-p3*(np.log(p3)/np.log(3))
    
    # for i in range (h):
    #     if(p1[i] != 0 and p2[i] != 0 and p3[i] != 0):
    #         h[i] = -p1*(np.log(p1)/np.log(3))-p2*(np.log(p2)/np.log(3))-p3*(np.log(p3)/np.log(3))
    #     else:
    #         h[i] = -1
    
    #h[(p1 != 0) and (p2 != 0) and (p3 != 0)] = -p1*(np.log(p1)/np.log(3))-p2*(np.log(p2)/np.log(3))-p3*(np.log(p3)/np.log(3))
    #h[(p1 == 0) or (p2 == 0) or (p3 == 0)] = -1

    return h

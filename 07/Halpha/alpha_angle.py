# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: elpha_angle.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and Communications Technology
#==================================================================================

import numpy as np
from os import path
from ywanalysis import saveHistogram


def calculate_alpha_angle(eig_1,eig_2,eig_3):
    """
    オンライン学習2　SAR画像解析応用編
    
    固有値からアルファ角を計算します
    :param eig_1: 固有値行列1
    :param eig_2: 固有値行列2
    :param eig_3: 固有値行列3
    
    :return: アルファ角
    """
    
    p1 = eig_1 / (eig_1 + eig_2 + eig_3)
    p2 = eig_2 / (eig_1 + eig_2 + eig_3)
    p3 = eig_3 / (eig_1 + eig_2 + eig_3)
    
    # replace inf and nan with 0
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(p1)
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(p2)
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(p3)
    
    alpha = p1 * 0 + p2 * (np.pi / 2) + p3 * (np.pi / 2)

    return alpha
    
    
def calculate_alpha_angleYW(eig_1,eig_2,eig_3, evector):
    """
    オンライン学習2　SAR画像解析応用編
    
    固有値からアルファ角を計算します
    :param eig_1: 固有値行列1
    :param eig_2: 固有値行列2
    :param eig_3: 固有値行列3
    
    :return: アルファ角
    """
    
    p1 = eig_1 / (eig_1 + eig_2 + eig_3)
    p2 = eig_2 / (eig_1 + eig_2 + eig_3)
    p3 = eig_3 / (eig_1 + eig_2 + eig_3)
    
    ev1 = evector[:, 0:1, 0:1].reshape(p1.shape)
    ev2 = evector[:, 0:1, 1:2].reshape(p2.shape)
    ev3 = evector[:, 0:1, 2:3].reshape(p3.shape)
    
    print("ev max")
    print(ev1.max())
    print(ev2.max())
    print(ev3.max())

    print("ev min")
    print(ev1.min())
    print(ev2.min())
    print(ev3.min())
    
    evhist = np.histogram(ev1, 100, (-1.0, 1.0))
    #outdir = '/mnt/nfsdir/usr4/workspace/output/alphaentropy/'
    saveHistogram("ev1hist.txt", evhist)
    
    # replace inf and nan with 0
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(p1)
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(p2)
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(p3)
    
    a0 = np.arccos(np.abs(ev1))
    a1 = np.arccos(np.abs(ev2))
    a2 = np.arccos(np.abs(ev3))
    
    #alpha = p1 * 0 + p2 * (np.pi / 2) + p3 * (np.pi / 2)
    alpha = p1 * a0 + p2 * a1 + p3 * a2

    return alpha

# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: anisotropy.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and Communications Technology
#==================================================================================

import numpy as np
from os import path


def calculate_anisotropy(eig2,eig3):
    """
    オンライン学習2　SAR画像解析応用編
    
    固有値からAnisotropyを計算します
    :param eig_2: 固有値行列2
    :param eig_3: 固有値行列3
    
    :return: Anisotropy
    """
    
    return (eig2 - eig3) / (eig2 + eig3)
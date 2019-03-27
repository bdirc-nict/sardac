# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: eigen_value.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and Communications Technology
#==================================================================================

import numpy as np
from os import path


def calculate_eigen_value(c_11,c_12,c_13,c_21,c_22,c_23,c_31,c_32,c_33):
    """
    オンライン学習2　SAR画像解析応用編
    
    Covariance行列から固有値を計算します
    :param c_11: Covariance 行列(11成分)
    :param c_12: Covariance 行列(12成分)
    :param c_13: Covariance 行列(13成分)
    :param c_21: Covariance 行列(21成分)
    :param c_22: Covariance 行列(22成分)
    :param c_23: Covariance 行列(23成分)
    :param c_31: Covariance 行列(31成分)
    :param c_32: Covariance 行列(32成分)
    :param c_33: Covariance 行列(33成分)
    :return: 固有値
    """
    
    # Transform the matrix
    matrix_1 = np.dstack([c_11.reshape(c_11.size,1),c_12.reshape(c_12.size,1),c_13.reshape(c_13.size,1)])
    matrix_2 = np.dstack([c_21.reshape(c_21.size,1),c_22.reshape(c_22.size,1),c_23.reshape(c_23.size,1)])
    matrix_3 = np.dstack([c_31.reshape(c_31.size,1),c_32.reshape(c_32.size,1),c_33.reshape(c_33.size,1)])
    
    matrix = (np.stack([matrix_1,matrix_2,matrix_3],1)).reshape(c_11.size,3,3)
    
    value,vector = np.linalg.eig(matrix)
    eig_1 = value[:,0].reshape(*c_11.shape)
    eig_2 = value[:,1].reshape(*c_11.shape)
    eig_3 = value[:,2].reshape(*c_11.shape)
    
    return eig_1,eig_2,eig_3
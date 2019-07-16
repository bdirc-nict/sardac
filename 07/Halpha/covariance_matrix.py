# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: coherency_matrix.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

import numpy as np
from os import path
import cv2


def create_covariance_matrix(hh, hv, vv, win_az, win_gr):
    """
    オンライン学習2　SAR画像解析応用編
    
    散乱行列からCovariance行列を生成します
    :param hh: 散乱行列(HH成分)
    :param hv: 散乱行列(HV成分)
    :param vv: 散乱行列(VV成分)
    :param win_az: マルチルック数（Az方向）
    :param win_gr: マルチルック数（Gr方向）
    :return: Covariance行列
    """
    
    c_11 = hh*hh.conjugate()
    c_12 = hh*hv.conjugate()
    c_13 = hh*vv.conjugate()
    c_21 = hv*hh.conjugate()
    c_22 = hv*hv.conjugate()
    c_23 = hv*vv.conjugate()
    c_31 = vv*hh.conjugate()
    c_32 = vv*hv.conjugate()
    c_33 = vv*vv.conjugate()
    
    # Multilook
    if win_az == 1 and win_gr == 1:
        #c_11.real = cv2.blur(c_11.real,(win_az,win_gr))
        c_12.real = np.sqrt(2)*c_12.real
        #c_13.real = cv2.blur(c_13.real,(win_az,win_gr))
        c_21.real = np.sqrt(2)*c_21.real
        c_22.real = 2*c_22.real
        c_23.real = np.sqrt(2)*c_23.real
        #c_31.real = cv2.blur(c_31.real,(win_az,win_gr))
        c_32.real = np.sqrt(2)*c_32.real
        #c_33.real = cv2.blur(c_33.real,(win_az,win_gr))
        #c_11.imag = cv2.blur(c_11.imag,(win_az,win_gr))
        c_12.imag = np.sqrt(2)*c_12.imag
        #c_13.imag = cv2.blur(c_13.imag,(win_az,win_gr))
        c_21.imag = np.sqrt(2)*c_21.imag
        c_22.imag = 2*c_22.imag
        c_23.imag = np.sqrt(2)*c_23.imag
        #c_31.imag = cv2.blur(c_31.imag,(win_az,win_gr))
        c_32.imag = np.sqrt(2)*c_32.imag
        #c_33.imag = cv2.blur(c_33.imag,(win_az,win_gr))
        
    else:
        c_11.real = cv2.blur(c_11.real,(win_az,win_gr))
        c_12.real = np.sqrt(2)*cv2.blur(c_12.real,(win_az,win_gr))
        c_13.real = cv2.blur(c_13.real,(win_az,win_gr))
        c_21.real = np.sqrt(2)*cv2.blur(c_21.real,(win_az,win_gr))
        c_22.real = 2*cv2.blur(c_22.real,(win_az,win_gr))
        c_23.real = np.sqrt(2)*cv2.blur(c_23.real,(win_az,win_gr))
        c_31.real = cv2.blur(c_31.real,(win_az,win_gr))
        c_32.real = np.sqrt(2)*cv2.blur(c_32.real,(win_az,win_gr))
        c_33.real = cv2.blur(c_33.real,(win_az,win_gr))
        c_11.imag = cv2.blur(c_11.imag,(win_az,win_gr))
        c_12.imag = np.sqrt(2)*cv2.blur(c_12.imag,(win_az,win_gr))
        c_13.imag = cv2.blur(c_13.imag,(win_az,win_gr))
        c_21.imag = np.sqrt(2)*cv2.blur(c_21.imag,(win_az,win_gr))
        c_22.imag = 2*cv2.blur(c_22.imag,(win_az,win_gr))
        c_23.imag = np.sqrt(2)*cv2.blur(c_23.imag,(win_az,win_gr))
        c_31.imag = cv2.blur(c_31.imag,(win_az,win_gr))
        c_32.imag = np.sqrt(2)*cv2.blur(c_32.imag,(win_az,win_gr))
        c_33.imag = cv2.blur(c_33.imag,(win_az,win_gr))
    

    return c_11,c_12,c_13,c_21,c_22,c_23,c_31,c_32,c_33

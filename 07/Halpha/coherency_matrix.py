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


def create_coherency_matrix(hh, hv, vv, win_az, win_gr):
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
    
    HplusV = hh + vv
    HminusV = hh - vv
    T_11 = HplusV * HplusV.conjugate()
    T_12 = HplusV*HminusV.conjugate()
    T_13 = 2*hv.conjugate() * HplusV
    T_21 = HminusV * HplusV.conjugate()
    T_22 = HminusV * HminusV.conjugate()
    T_23 = 2*hv.conjugate() * HminusV
    T_31 = 2*hv*HplusV.conjugate()
    T_32 = 2*hv * HminusV.conjugate()
    T_33 = 4*hv*hv.conjugate()
    
      # Multilook
    T_11.real = cv2.blur(T_11.real,(win_az,win_gr)) /2 
    T_12.real = cv2.blur(T_12.real,(win_az,win_gr)) /2 
    T_13.real = cv2.blur(T_13.real,(win_az,win_gr)) /2 
    T_21.real = cv2.blur(T_21.real,(win_az,win_gr)) /2 
    T_22.real = cv2.blur(T_22.real,(win_az,win_gr)) /2 
    T_23.real = cv2.blur(T_23.real,(win_az,win_gr)) /2 
    T_31.real = cv2.blur(T_31.real,(win_az,win_gr)) /2 
    T_32.real = cv2.blur(T_32.real,(win_az,win_gr)) /2 
    T_33.real = cv2.blur(T_33.real,(win_az,win_gr)) /2 
    T_11.imag = cv2.blur(T_11.imag,(win_az,win_gr)) /2 
    T_12.imag = cv2.blur(T_12.imag,(win_az,win_gr)) /2 
    T_13.imag = cv2.blur(T_13.imag,(win_az,win_gr)) /2 
    T_21.imag = cv2.blur(T_21.imag,(win_az,win_gr)) /2 
    T_22.imag = cv2.blur(T_22.imag,(win_az,win_gr)) /2 
    T_23.imag = cv2.blur(T_23.imag,(win_az,win_gr)) /2 
    T_31.imag = cv2.blur(T_31.imag,(win_az,win_gr)) /2 
    T_32.imag = cv2.blur(T_32.imag,(win_az,win_gr)) /2 
    T_33.imag = cv2.blur(T_33.imag,(win_az,win_gr)) /2 
    
    return T_11,T_12,T_13,T_21,T_22,T_23,T_31,T_32,T_33

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
    """
# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: four_component.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

import numpy as np
from os import path
import cv2
#G4U法の実装YW

def G4U_decomposition(T_11, T_12, T_13, T_21, T_22, T_23, T_31, T_32, T_33, win_az, win_gr):

    ps = np.zeros(T_11.shape,dtype=np.float32)
    pd = np.zeros(T_11.shape,dtype=np.float32)
    pv = np.zeros(T_11.shape,dtype=np.float32)
    S = np.zeros(T_11.shape,dtype=np.float32)
    D = np.zeros(T_11.shape,dtype=np.float32)
    C = np.zeros(T_11.shape,dtype=np.float32)
    C_0 = np.zeros(T_11.shape,dtype=np.float32)
    C_1 = np.zeros(T_11.shape,dtype=np.float32)
    cos2t = np.zeros(T_11.shape,dtype=np.float32)
    sin2t = np.zeros(T_11.shape,dtype=np.float32)
    #TP = np.zeros(T_11.shape,dtype=np.float32)

    TP = T_11 + T_22 + T_33
    pc = 2 * np.abs(cv2.blur(T_23.imag,(win_az,win_gr)))
    
    thetax2 = np.arctan(2.0* T_23.real / (T_22 - T_33) ) / 2.0
    print(thetax2.shape)
    cos2t = np.cos(thetax2)
    sin2t = np.sin(thetax2)
    
    T_22Theta = cos2t*(cos2t*T_22+sin2t*T_32)+sin2t*(cos2t*T_23+sin2t*T_33)
    T_33Theta = -sin2t*(-sin2t*T_22+cos2t*T_32) + cos2t*(-sin2t*T_23+cos2t*T_33)
    T_12Theta = cos2t * T_21 + sin2t* T_31
    T_13Theta = -sin2t*T_21 + cos2t * T_31
    """
    #間違い
    T_22Theta = cos2theta * T_22 * cos2theta
    T_33Theta = cos2theta * T_33 * cos2theta
    """
    C_0 = 2.0 * T_11 + pc - TP
    C_1 = T_11 - T_22Theta + 7.0/8.0*T_33Theta + pc / 16.0
    
    #C_1 > 0の時とき
    db = (T_11 + T_22Theta - 2*T_12Theta.real) / (T_11 + T_22Theta + 2*T_12Theta.real)
    #print(db.dtype)
    
    x = np.vectorize(lambda x: (np.log10(x) * 10 if x > 0 else -np.inf))(db.real)
    
       # x < -2
    pv[(C_1 > 0) & (x < -2)] = (15/8) * (2.0* T_33Theta[(C_1 > 0) &(x<-2)] - pc[(C_1 > 0) &(x<-2)]).real
    # x < -2 & pv < 0
    #pv[(C_1 > 0) &(x < -2) & (pv < 0)] = (15/2) * abs_hv[(C_1 > 0) &(x < -2) & (pv < 0)]
    pv[(C_1 > 0) &(x < -2) & (pv < 0)] = (15/8) * (2.0* T_33Theta[(C_1 > 0) &(x < -2) & (pv < 0)]).real
    pc[(C_1 > 0) &(x < -2) & (pv < 0)] = 0
    # x < -2
    #a[(C_1 > 0) &x < -2] = abs_hh[(C_1 > 0) &x < -2] - 4*abs_hv[(C_1 > 0) &x < -2] + (3/4) * pc[(C_1 > 0) &x < -2]
    #b[(C_1 > 0) &x < -2] = abs_vv[(C_1 > 0) &x < -2] - (3/2)*abs_hv[(C_1 > 0) &x < -2] + (1/8) * pc[(C_1 > 0) &x < -2]
    
    # x > 2
    pv[(C_1 > 0) &(x > 2)] = (15/8) * (2.0* T_33Theta[(C_1 > 0) &(x > 2)] - pc[(C_1 > 0) &(x > 2)]).real
    # x > 2 & pv < 0
    #pv[(C_1 > 0) &(x > 2) & (pv < 0)] = (15/2) * abs_hv[(C_1 > 0) &(x > 2) & (pv < 0)]
    pv[(C_1 > 0) &(x > 2) & (pv < 0)] = (15/8) * (2.0* T_33Theta[(C_1 > 0) &(x > 2) & (pv < 0)]).real
    pc[(C_1 > 0) &(x > 2) & (pv < 0)] = 0
    # x > 2
    #a[(C_1 > 0) &x > 2] = abs_hh[(C_1 > 0) &x > 2] - (3/2) * abs_hv[(C_1 > 0) &x > 2] + (1/8) * pc[(C_1 > 0) &x > 2]
    #b[(C_1 > 0) &x > 2] = abs_vv[(C_1 > 0) &x > 2] - 4 * abs_hv[(C_1 > 0) &x > 2] + (3/4) * pc[(C_1 > 0) &x > 2]
    
    # x >= -2 & x <= 2
    pv[(C_1 > 0) &(x >= -2) & (x <= 2)] = (2.0) * (2.0* T_33Theta[(C_1 > 0) &(x >= -2) & (x <= 2)] - pc[(C_1 > 0) &(x >= -2) & (x <= 2)]).real
    # x >= -2 & x <= 2 & pv < 0
    #pv[(C_1 > 0) &(x >= -2) & (x <= 2) & (pv < 0)] = 8 * abs_hv[(C_1 > 0) &(x >= -2) & (x <= 2) & (pv < 0)]
    pv[(C_1 > 0) &(x >= -2) & (x <= 2) & (pv < 0)] = (2.0) * (2.0* T_33Theta[(C_1 > 0) &(x >= -2) & (x <= 2) & (pv < 0)]).real
    pc[(C_1 > 0) &(x >= -2) & (x <= 2) & (pv < 0)] = 0
    
    #C_1 <=0のとき
    pv[C_1<=0] = 15.0 / 16.0 *(2.0*T_33Theta[C_1<=0] - pc[C_1<=0]).real
    pc[(C_1 <= 0) & (pv < 0)] = 0;
    pv[(C_1 <= 0) & (pv < 0)] = 15.0 / 16.0 * (2.0*T_33Theta[(C_1 <= 0) & (pv < 0)].real)
    
    
    S[C_1 > 0] = T_11[C_1 > 0] - pv[C_1 > 0] / 2.0;
    S[C_1<= 0] = T_11[C_1<= 0]
    D = TP - pv - pc - S
    C[(C_1 > 0) & (x >= -2) & (x <= 2)] = T_12Theta[(C_1 > 0) & (x >= -2) & (x <= 2)] + T_13Theta[(C_1 > 0) & (x >= -2) & (x <= 2)]
    C[(C_1 > 0) & (x < -2)]             = T_12Theta[(C_1 > 0) & (x < -2)] + T_13Theta[(C_1 > 0) & (x < -2)] - pv[(C_1 > 0) & (x < -2)] / 6.0
    C[(C_1 > 0) & (x > 2) ]             = T_12Theta[(C_1 > 0) & (x > 2) ] + T_13Theta[(C_1 > 0) & (x > 2) ] + pv[(C_1 > 0) & (x > 2) ] / 6.0
    C[(C_1 <=0)]                        = T_12Theta[(C_1 <=0)] + T_13Theta[(C_1 <=0)]
    
    flg = pv + pc
    
    ps[(C_1 > 0) &(flg <= TP)&(C_0 > 0)] = S[(C_1 > 0) &(flg <= TP)&(C_0 > 0)] + C[(C_1 > 0) &(flg <= TP)&(C_0 > 0)]*C[(C_1 > 0) &(flg <= TP)&(C_0 > 0)].conjugate() / S[(C_1 > 0) &(flg <= TP)&(C_0 > 0)]
    pd[(C_1 > 0) &(flg <= TP)&(C_0 > 0)] = D[(C_1 > 0) &(flg <= TP)&(C_0 > 0)] - C[(C_1 > 0) &(flg <= TP)&(C_0 > 0)]*C[(C_1 > 0) &(flg <= TP)&(C_0 > 0)].conjugate() / S[(C_1 > 0) &(flg <= TP)&(C_0 > 0)]
 
    ps[(C_1 > 0) &(flg <= TP)&(C_0<= 0)] = S[(C_1 > 0) &(flg <= TP)&(C_0<= 0)] - C[(C_1 > 0) &(flg <= TP)&(C_0<= 0)]*C[(C_1 > 0) &(flg <= TP)&(C_0<= 0)].conjugate() / D[(C_1 > 0) &(flg <= TP)&(C_0<= 0)]
    pd[(C_1 > 0) &(flg <= TP)&(C_0<= 0)] = D[(C_1 > 0) &(flg <= TP)&(C_0<= 0)] + C[(C_1 > 0) &(flg <= TP)&(C_0<= 0)]*C[(C_1 > 0) &(flg <= TP)&(C_0<= 0)].conjugate() / D[(C_1 > 0) &(flg <= TP)&(C_0<= 0)]
    
    #最終判断
    ps[(C_1 > 0) &(flg <= TP)&(ps >0 ) & (pd <0)] = TP[(C_1 > 0) &(flg <= TP)&(ps >0 ) & (pd <0)] - pv[(C_1 > 0) &(flg <= TP)&(ps >0 ) & (pd <0)] - pc[(C_1 > 0) &(flg <= TP)&(ps >0 ) & (pd <0)]
    pd[(C_1 > 0) &(flg <= TP)&(ps >0 ) & (pd <0)] = 0

    ps[(C_1 > 0) &(flg <= TP)&(ps <0 ) & (pd >0)] = 0
    pd[(C_1 > 0) &(flg <= TP)&(ps <0 ) & (pd >0)] = TP[(C_1 > 0) &(flg <= TP)&(ps <0 ) & (pd >0)] - pv[(C_1 > 0) &(flg <= TP)&(ps <0 ) & (pd >0)] - pc[(C_1 > 0) &(flg <= TP)&(ps <0 ) & (pd >0)]


    # flg > tp
    ps[(C_1 > 0) &(flg > TP)] = 0
    pd[(C_1 > 0) &(flg > TP)] = 0
    pv[(C_1 > 0) &(flg > TP)] = TP[(C_1 > 0) &(flg > TP)] - pc[(C_1 > 0) &(flg > TP)]
    
    
    ps[(C_1 <= 0)] = S[(C_1 <= 0)] - C[(C_1 <= 0)]*C[(C_1 <= 0)].conjugate() / D[(C_1 <= 0)]
    pd[(C_1 <= 0)] = D[(C_1 <= 0)] + C[(C_1 <= 0)]*C[(C_1 <= 0)].conjugate() / D[(C_1 <= 0)]
    
    #最終判断
    ps[(C_1 <= 0) &(ps >0 ) & (pd <0)] = TP[(C_1 <= 0) &(ps >0 ) & (pd <0)] - pv[(C_1 <= 0) &(ps >0 ) & (pd <0)] - pc[(C_1 <= 0) &(ps >0 ) & (pd <0)]
    pd[(C_1 <= 0) &(ps >0 ) & (pd <0)] = 0

    ps[(C_1 <= 0) &(ps <0 ) & (pd >0)] = 0
    pd[(C_1 <= 0) &(ps <0 ) & (pd >0)] = TP[(C_1 <= 0) &(ps <0 ) & (pd >0)] - pv[(C_1 <= 0) &(ps <0 ) & (pd >0)] - pc[(C_1 <= 0) &(ps <0 ) & (pd >0)]

    """
    # x < -2
    pv[x < -2] = (15/8) * (2.0* T_33Theta[x<-2] - pc[x<-2])
    # x < -2 & pv < 0
    #pv[(x < -2) & (pv < 0)] = (15/2) * abs_hv[(x < -2) & (pv < 0)]
    pv[(x < -2) & (pv < 0)] = (15/8) * (2.0* T_33Theta[x<-2])
    pc[(x < -2) & (pv < 0)] = 0
    # x < -2
    #a[x < -2] = abs_hh[x < -2] - 4*abs_hv[x < -2] + (3/4) * pc[x < -2]
    #b[x < -2] = abs_vv[x < -2] - (3/2)*abs_hv[x < -2] + (1/8) * pc[x < -2]
    
    # x > 2
    pv[x > 2] = (15/8) * (2.0* T_33Theta[x<-2] - pc[x<-2])
    # x > 2 & pv < 0
    #pv[(x > 2) & (pv < 0)] = (15/2) * abs_hv[(x > 2) & (pv < 0)]
    pv[(x > 2) & (pv < 0)] = (15/8) * (2.0* T_33Theta[x<-2])
    pc[(x > 2) & (pv < 0)] = 0
    # x > 2
    #a[x > 2] = abs_hh[x > 2] - (3/2) * abs_hv[x > 2] + (1/8) * pc[x > 2]
    #b[x > 2] = abs_vv[x > 2] - 4 * abs_hv[x > 2] + (3/4) * pc[x > 2]
    
    # x >= -2 & x <= 2
    pv[(x >= -2) & (x <= 2)] = (2.0) * (2.0* T_33Theta[x<-2] - pc[x<-2])
    # x >= -2 & x <= 2 & pv < 0
    #pv[(x >= -2) & (x <= 2) & (pv < 0)] = 8 * abs_hv[(x >= -2) & (x <= 2) & (pv < 0)]
    pv[(x >= -2) & (x <= 2) & (pv < 0)] = (2.0) * (2.0* T_33Theta[x<-2])
    pc[(x >= -2) & (x <= 2) & (pv < 0)] = 0
    
    S[C_1 >0]   = T_11 - pv / 2.0;
    S[C_1 <= 0] = T_11
    D = TP - pv - pc - S
    C[(C_1>0) & (x >= -2) & (x <= 2)] = T_12Theta + T_13Theta
    C[(C_1>0) & (x < -2)]             = T_12Theta + T_13Theta - pv / 6.0
    C[(C_1>0) & (x > 2) ]             = T_12Theta + T_13Theta + pv / 6.
    
    flg = pv + pc
    
  

    ps[(fig <= TP)&(C_0 > 0)] = S + C*C.conjugate() / S
    pd[(fig <= TP)&(C_0 > 0)] = D - C*C.conjugate() / S
 
    ps[(fig <= TP)&(C_0<= 0)] = S - C*C.conjugate() / D
    pd[(fig <= TP)&(C_0<= 0)] = D + C*C.conjugate() / D
   
    # flg > tp
    ps[flg > TP] = 0
    pd[flg > TP] = 0
    pv[flg > TP] = TP[flg > TP] - pc[flg > TP]
    """
    
    return ps,pd,pv,pc

    """
    オンライン学習2　SAR画像解析応用編
    
    四成分散乱モデル分解法を適用します
    :param hh: 散乱行列(HH成分)
    :param hv: 散乱行列(HV成分)
    :param vv: 散乱行列(VV成分)
    :param win_az: マルチルック数（Az方向）
    :param win_gr: マルチルック数（Gr方向）
    :return: 四成分散乱電力
             ps(表面散乱)
             pd(二回反射散乱)
             pv(体積散乱)
             pc(へリックス散乱)
    """
    
    """
    # Pc Power
    pc = 2 * np.abs(cv2.blur(((hh-vv)*hv.conjugate()).imag,(win_az,win_gr)))
    
    abs_hh = cv2.blur((hh*hh.conjugate()).real,(win_az,win_gr))
    abs_hv = cv2.blur((hv*hv.conjugate()).real,(win_az,win_gr))
    abs_vv = cv2.blur((vv*vv.conjugate()).real,(win_az,win_gr))
    
    x = np.vectorize(lambda x: (np.log10(x) * 10 if x > 0 else -np.inf))(abs_vv / abs_hh)
    
    # Total Power
    tp = abs_hh + abs_vv + 2*abs_hv
    
    ps = np.zeros(hh.shape,dtype=np.float32)
    pd = np.zeros(hh.shape,dtype=np.float32)
    pv = np.zeros(hh.shape,dtype=np.float32)
    a = np.zeros(hh.shape,dtype=np.float32)
    b = np.zeros(hh.shape,dtype=np.float32)
    alpha = np.zeros(hh.shape,dtype=np.complex64)
    beta = np.zeros(hh.shape,dtype=np.complex64)
    fs = np.zeros(hh.shape,dtype=np.float32)
    fd = np.zeros(hh.shape,dtype=np.float32)
    c0 = np.zeros(hh.shape,dtype=np.complex64)
    
    # x < -2
    pv[x < -2] = (15/2) * abs_hv[x < -2] - (15/8) * pc[x < -2]
    # x < -2 & pv < 0
    pv[(x < -2) & (pv < 0)] = (15/2) * abs_hv[(x < -2) & (pv < 0)]
    pc[(x < -2) & (pv < 0)] = 0
    # x < -2
    a[x < -2] = abs_hh[x < -2] - 4*abs_hv[x < -2] + (3/4) * pc[x < -2]
    b[x < -2] = abs_vv[x < -2] - (3/2)*abs_hv[x < -2] + (1/8) * pc[x < -2]
    
    # x > 2
    pv[x > 2] = (15/2) * abs_hv[x > 2] - (15/8) * pc[x > 2]
    # x > 2 & pv < 0
    pv[(x > 2) & (pv < 0)] = (15/2) * abs_hv[(x > 2) & (pv < 0)]
    pc[(x > 2) & (pv < 0)] = 0
    # x > 2
    a[x > 2] = abs_hh[x > 2] - (3/2) * abs_hv[x > 2] + (1/8) * pc[x > 2]
    b[x > 2] = abs_vv[x > 2] - 4 * abs_hv[x > 2] + (3/4) * pc[x > 2]
    
    # x >= -2 & x <= 2
    pv[(x >= -2) & (x <= 2)] = 8 * abs_hv[(x >= -2) & (x <= 2)] - 2 * pc[(x >= -2) & (x <= 2)]
    # x >= -2 & x <= 2 & pv < 0
    pv[(x >= -2) & (x <= 2) & (pv < 0)] = 8 * abs_hv[(x >= -2) & (x <= 2) & (pv < 0)]
    pc[(x >= -2) & (x <= 2) & (pv < 0)] = 0
    # x >= -2 & x <= 2
    a[(x >= -2) & (x <= 2)] = abs_hh[(x >= -2) & (x <= 2)] - 3 * abs_hv[(x >= -2) & (x <= 2)] + (1/2) * pc[(x >= -2) & (x <= 2)]
    b[(x >= -2) & (x <= 2)] = abs_vv[(x >= -2) & (x <= 2)] - 3 * abs_hv[(x >= -2) & (x <= 2)] + (1/2) * pc[(x >= -2) & (x <= 2)]
    
    flg = pv + pc
    
    # flg > tp
    ps[flg > tp] = 0
    pd[flg > tp] = 0
    pv[flg > tp] = tp[flg > tp] - pc[flg > tp]
    
    # flg <= tp
    temp = hh * vv.conjugate()
    temp.real = cv2.blur(temp.real,(win_az,win_gr))
    temp.imag = cv2.blur(temp.imag,(win_az,win_gr))
    
    c0[flg <= tp] =  temp[flg <= tp] - abs_hv[flg <= tp] + (1/2) * pc[flg <= tp]
    c0_temp = cv2.blur((c0 * c0.conjugate()).real,(win_az,win_gr))
    # flg <= tp & c0 > 0
    alpha[(flg <= tp) & (c0.real > 0)] = -1
    fd[(flg <= tp) & (c0.real > 0)] = (a[(flg <= tp) & (c0.real > 0)] * b[(flg <= tp) & (c0.real > 0)] \
    - (c0_temp[(flg <= tp) & (c0.real > 0)])) / (a[(flg <= tp) & (c0.real > 0)] + b[(flg <= tp) & (c0.real > 0)] + 2 * c0_temp[(flg <= tp) & (c0.real > 0)])
    fs[(flg <= tp) & (c0.real > 0)] = b[(flg <= tp) & (c0.real > 0)] - fd[(flg <= tp) & (c0.real > 0)]
    beta[(flg <= tp) & (c0.real > 0)] = (c0[(flg <= tp) & (c0.real > 0)] + fd[(flg <= tp) & (c0.real > 0)]) / fs[(flg <= tp) & (c0.real > 0)]
    
    # flg <= tp & c0 <= 0
    beta[(flg <= tp) & (c0.real <= 0)] = 1
    
    fs[(flg <= tp) & (c0.real <= 0)] = (a[(flg <= tp) & (c0.real <= 0)] * b[(flg <= tp) & (c0.real <= 0)] \
    - (c0_temp[(flg <= tp) & (c0.real <= 0)])) / (a[(flg <= tp) & (c0.real <= 0)] + b[(flg <= tp) & (c0.real <= 0)] - 2 * c0_temp[(flg <= tp) & (c0.real <= 0)])
    fd[(flg <= tp) & (c0.real <= 0)] = a[(flg <= tp) & (c0.real <= 0)] - fs[(flg <= tp) & (c0.real <= 0)]
    alpha[(flg <= tp) & (c0.real <= 0)] = (c0[(flg <= tp) & (c0.real <= 0)].conjugate() - fs[(flg <= tp) & (c0.real <= 0)]) / fd[(flg <= tp) & (c0.real <= 0)]
    
    beta_temp = cv2.blur((beta * beta.conjugate()).real,(win_az,win_gr))
    alpha_temp = cv2.blur((alpha * alpha.conjugate()).real,(win_az,win_gr))
    
    ps[(flg <= tp)] = fs[(flg <= tp)] * (1 + beta_temp[(flg <= tp)])
    pd[(flg <= tp)] = fd[(flg <= tp)] * (1 + alpha_temp[(flg <= tp)])
    
    # flg <= tp & ps > 0 &pd < 0
    pd[(flg <= tp) & (ps>0) & (pd<0)] = 0
    ps[(flg <= tp) & (ps>0) & (pd<0)] = tp[(flg <= tp)&(ps>0)&(pd<0)] - pv[(flg <= tp)&(ps>0)&(pd<0)] - pc[(flg <= tp)&(ps>0)&(pd<0)]
    
    # flg <= tp & ps < 0 &pd > 0
    ps[(flg <= tp) & (ps<0) & (pd>0)] = 0
    pd[(flg <= tp) & (ps<0) & (pd>0)] = tp[(flg <= tp)&(ps>0)&(pd<0)] - pv[(flg <= tp)&(ps>0)&(pd<0)] - pc[(flg <= tp)&(ps>0)&(pd<0)]
    
    # replace negative values to 0
    ps[ps < 0] = 0
    pd[pd < 0] = 0
    pv[pv < 0] = 0
    pc[pc < 0] = 0
    
    return ps,pd,pv,pc
    """
    
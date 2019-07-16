# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: create_comp_image.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

import numpy as np
from Common.mgp_info_reader import read_mgp_info, get_data, get_decimal_from_sexagesimal
from Common.gdal_command import gdaltranslate_gcp, gdalwarp
from scattering_matrix import create_scattering_matrix
from covariance_matrix import create_covariance_matrix
from coherency_matrix import create_coherency_matrix
from entropy import calculate_entropy
from eigen_value import calculate_eigen_value
from four_component import four_component_decomposition
from G4U import G4U_decomposition #YW
from alpha_angle import calculate_alpha_angle
from anisotropy import calculate_anisotropy

from Common.constant import DEV_FLAG, DATA_PATH_BASE, IMAGE_FLOAT

from tifffile import imsave

from math import ceil, log10
from os import path, makedirs, remove
import time
from ywanalysis import saveHistogram


format_name = "GTiff"
mgp_key = "mgp_key"


def create_comp_image(in_hh, in_hv, in_vv, in_info, ot_dir, win_az, win_gr):
    """
    Create an image from raw SAR image data.
    :param in_hh: HH band data file of SAR image data
    :param in_hv: HV band data file of SAR image data
    :param in_vv: VV band data file of SAR image data
    :param in_info: SAR observation specification file
    :param ot_dir: The destination path
    :param win_az: Multillok size of AZ direction
    :param win_gr: Multillok size of GR direction
    """

    # Get destination file name
    filename = path.splitext(path.basename(in_hh))[0]
    if filename.lower().startswith("sendai"):
        basename = "Sendai"
    elif filename.lower().startswith("obs15"):
        basename = "Kumamoto"
    elif filename.lower().startswith("obs09"):
        basename = "Kumamoto"
    else:
        basename = filename

    # Get actual file path
    in_hh = path.join(DATA_PATH_BASE, in_hh)
    in_hv = path.join(DATA_PATH_BASE, in_hv)
    in_vv = path.join(DATA_PATH_BASE, in_vv)
    in_info = path.join(DATA_PATH_BASE, in_info)
    ot_dir = path.join(DATA_PATH_BASE, ot_dir)
    makedirs(ot_dir, exist_ok=True)

    fn_single = path.join(ot_dir, "tmp_{0}_G4U_base.tif".format(basename))
    fn_single_trans = path.join(ot_dir, "tmp_{0}_trans.tif".format(basename))

    read_mgp_info(mgp_key, in_info)
    
    n_az = int(get_data(mgp_key, "IMAGE_SIZE_AZ"))
    n_gr = int(get_data(mgp_key, "IMAGE_SIZE_GR"))
    n_img_az = ceil(n_az / win_az)
    n_img_gr = ceil(n_gr / win_gr)

    # Read raw SAR image data file.
    
    """
    オンライン学習１　SAR画像解析基礎編
    
    SARデータを読み込み、ﾏﾙﾁﾙｯｸを行った結果を複素数で出力します
    
    関数  : create_scattering_matrix
    引数1 : 入力ファイル(*.mgp_HHm　or *.mgp_HVm or *.mgp_VVm)
    引数2 : SARデータ画像サイズ(アジマス方向)
    引数3 : SARデータ画像サイズ(グランドレンジ方向)
    引数4 : マルチルックサイズ(アジマス方向)
    引数5 : マルチルックサイズ(グランドレンジ方向)
    
    返り値 : numpy complex64(複素数(実部：32bit,虚部：32bit))配列
    """
    print("band 1 read ...")
    hh = create_scattering_matrix(in_hh, n_az, n_gr, win_az, win_gr)
    print("band 2 read ...")
    hv = create_scattering_matrix(in_hv, n_az, n_gr, win_az, win_gr)
    print("band 3 read ...")
    vv = create_scattering_matrix(in_vv, n_az, n_gr, win_az, win_gr)
    
    
    # Create Coherency Matrix
    """
    オンライン学習2　SAR画像解析応用編
    
    散乱行列からCovariance行列を生成します
    
    関数  : create_covariance_matrix
    引数1 : 散乱行列(HH成分)
    引数2 : 散乱行列(HV成分)
    引数3 : 散乱行列(VV成分)
    引数4 : マルチルックサイズ(アジマス方向)
    引数5 : マルチルックサイズ(グランドレンジ方向)
    
    返り値 : covariance行列成分(複素数(実部：32bit,虚部：32bit))配列
    """
    
    print("Create Coherency Matrix ...")
    T_11,T_12,T_13,T_21,T_22,T_23,T_31,T_32,T_33 = create_coherency_matrix(hh,hv,vv,3,3)
    ps,pd,pv,pc = G4U_decomposition(T_11, T_12, T_13, T_21, T_22, T_23, T_31, T_32, T_33, 3, 3)

    logpd =np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pd)    
    logpv =np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pv)    
    logps =np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(ps)    
    pdhist = np.histogram(logpd, 100, (-100, 100))
    pvhist = np.histogram(logpv, 100, (-100, 100))
    pshist = np.histogram(logps, 100, (-100, 100))
    
    outdir = '/mnt/nfsdir/usr4/workspace/output/G4U/'
    saveHistogram(outdir+"pdhist.txt", pdhist)
    saveHistogram(outdir+"pvhist.txt", pvhist)
    saveHistogram(outdir+"pshist.txt", pshist)
  
    print(logpd.max())
    print(logpd.min())
    
    print("ps")
    print(ps.max())
    print(ps.min())
    print("pd")
    print(pd.max())
    print(pd.min())
    print("pv")
    print(pv.max())
    print(pv.min())
    
    
    rangeMin = -80
    rangeMax = 40
    
    #matrix_r = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pd))
    #matrix_g = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pv))
    #matrix_b = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(ps))
    #matrix_g = matrix_g * 1.2
  
    matrix_r = exband2Range(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(ps), rangeMin, rangeMax)
    #matrix_g = exband2RangeShift(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pv), rangeMin, rangeMax, 20)
    matrix_g = exband2Range(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pv), rangeMin, rangeMax)
    matrix_b = exband2Range(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pd), rangeMin, rangeMax)
    
    #oahist = np.histogram(alpha, 100, (0.0, 3.141592))

    
    print("save image")
    imsave(fn_single, np.stack([matrix_r, matrix_g, matrix_b]))
    print("save image end")
    exit(0)

    #print("Create Covariance Matrix ...")
    #c_11,c_12,c_13,c_21,c_22,c_23,c_31,c_32,c_33 = create_covariance_matrix(hh,hv,vv,3,3)
    
    """
    matrix_r = exband_histgram(np.vectorize(lambda x: (log10(x) * 10 if x != 0 else -np.inf))(c_11.real))
    matrix_g = exband_histgram(np.vectorize(lambda x: (log10(x) * 10 if x != 0 else -np.inf))(c_22.real))
    matrix_b = exband_histgram(np.vectorize(lambda x: (log10(x) * 10 if x != 0 else -np.inf))(c_33.real))
    """
    # Four Component Decomposition
    """
    オンライン学習2　SAR画像解析応用編
    
    四成分散乱モデル分解法を適用します
    
    関数  : four_component_decomposition
    引数1 : 散乱行列(HH成分)
    引数2 : 散乱行列(HV成分)
    引数3 : 散乱行列(VV成分)
    引数4 : マルチルックサイズ(アジマス方向)
    引数5 : マルチルックサイズ(グランドレンジ方向)
    
    返り値 : 四成分散乱電力(実数 32bit)配列
    """
    
    print("Four Component Decomposition ...")
    ps,pd,pv,pc = four_component_decomposition(hh,hv,vv,3,3)
    #= four_component_decomposition()
    
    logpd =np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pd)
    #matrix_r = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pd))
    #matrix_g = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pv))
    #matrix_b = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(ps))

    #truujou配色
    #rangeMin = -94.0
    #rangeMax = 67
    rangeMin = -62.0 + 16
    rangeMax = 35 - 16
    matrix_r = exband2Range(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pd), rangeMin, rangeMax)
    matrix_g = exband2Range(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(pv), rangeMin, rangeMax)
    matrix_b = exband2Range(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))(ps), rangeMin, rangeMax)
    #matrix_b = exband2Range(np.vectorize(lambda x: (log10(x)*0 if x > 0 else -np.inf))(ps), rangeMin, rangeMax)

    
    oHHhist = np.histogram(logpd, 240, (-120, 120))
    dirPath = '/mnt/nfsdir/usr4/workspace/result.mine/histogram/'
    saveHistogram(dirPath + "pdhist.txt", oHHhist)
    
    
    # Caluculate Eigen Value
    """
    オンライン学習2　SAR画像解析応用編
    
    Covariance行列から固有値を計算します
    
    関数  : calculate_eigen_value
    引数1 : covariance行列(C11成分)
    引数2 : covariance行列(C12成分)
    引数3 : covariance行列(C13成分)
    引数4 : covariance行列(C21成分)
    引数5 : covariance行列(C22成分)
    引数6 : covariance行列(C23成分)
    引数7 : covariance行列(C31成分)
    引数8 : covariance行列(C32成分)
    引数9 : covariance行列(C33成分)
    
    返り値 : 固有値(複素数(実部：32bit,虚部：32bit))配列
    """
    #print("Calculate Eigen Value ...")
    #= calculate_eigen_value()
    #eig_1,eig_2,eig_3 = calculate_eigen_value(c_11,c_12,c_13,c_21,c_22,c_23,c_31,c_32,c_33)
    """
    matrix_r = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))((eig_1*eig_1.conjugate()).real))
    matrix_g = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))((eig_2*eig_2.conjugate()).real))
    matrix_b = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))((eig_3*eig_3.conjugate()).real))
    """
    #matrix_r = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))())
    #matrix_g = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))())
    #matrix_b = exband_histgram(np.vectorize(lambda x: (log10(x)*10 if x > 0 else -np.inf))())

    # Calculate Entropy
    """
    オンライン学習2　SAR画像解析応用編
    
    固有値からエントロピーを計算します
    
    関数  : calculate_entropy
    引数1 : 固有値1
    引数2 : 固有値2
    引数3 : 固有値3
    
    返り値 : エントロピー(実数 32bit)配列
    """
    #print("Caluculate Entropy ...")
    #= calculate_entropy()
    #h = calculate_entropy(eig_1,eig_2,eig_3)
    
    # Calculate Alpah Angle
    """
    オンライン学習2　SAR画像解析応用編
    
    固有値からアルファ角を計算します
    
    関数  : calculate_alpha_angle
    引数1 : 固有値1
    引数2 : 固有値2
    引数3 : 固有値3
    
    返り値 : アルファ角(実数 32bit)配列
    """
    #print("Calculate Alpha Angle ...")
    #= calculate_alpha_angle()
    #alpha = calculate_alpha_angle(eig_1,eig_2,eig_3)

    
    # Calculate Anisotropy
    """
    オンライン学習2　SAR画像解析応用編
    
    固有値からAnisotropyを計算します
    
    関数  : calculate_anisotropy
    引数1 : 固有値2
    引数2 : 固有値3
    
    返り値 : Anisotropy(実数 32bit)配列
    """
    #print("Caluculate Anisotropy ...")
    #= calculate_anisotropy()
    #anisotropy = calculate_anisotropy(eig_2,eig_3)

    # Create Tiff image file.
    """
    オンライン学習１　SAR画像解析基礎編
    
    SAR二次元データを画像として出力します
    
    関数  : imsave
    引数1 : 出力ファイル名(*.tif)
    引数2 : SAR二次元データ
        RGB画像の場合にはnp.stack([R成分、G成分、B成分])
    """
    imsave(fn_single, np.stack([matrix_r, matrix_g, matrix_b]))
    #imsave(fn_single, exband_histgram(alpha))
    #imsave(fn_single, exband_histgram(anisotropy))

    # Create Geotiff file by "GDAL Translate".
    print("GDAL Translate ...")
    lonlat_ln = (get_decimal_from_sexagesimal(get_data(mgp_key, "LATE_NEAR_LONG")), get_decimal_from_sexagesimal(get_data(mgp_key, "LATE_NEAR_LAT")))
    lonlat_lf = (get_decimal_from_sexagesimal(get_data(mgp_key, "LATE_FAR_LONG")), get_decimal_from_sexagesimal(get_data(mgp_key, "LATE_FAR_LAT")))
    lonlat_en = (get_decimal_from_sexagesimal(get_data(mgp_key, "EARLY_NEAR_LONG")), get_decimal_from_sexagesimal(get_data(mgp_key, "EARLY_NEAR_LAT")))
    lonlat_ef = (get_decimal_from_sexagesimal(get_data(mgp_key, "EARLY_FAR_LONG")), get_decimal_from_sexagesimal(get_data(mgp_key, "EARLY_FAR_LAT")))
    gdaltranslate_gcp(fn_single_trans, fn_single,
                      [(0, 0, lonlat_ln[0], lonlat_ln[1]),
                       (0, n_img_gr-1, lonlat_lf[0], lonlat_lf[1]),
                       (n_img_az-1, 0, lonlat_en[0], lonlat_en[1]),
                       (n_img_az-1, n_img_gr-1, lonlat_ef[0], lonlat_ef[1])]
                      )

    # Execute "GDAL Warp".
    print("GDAL Warp ...")
    fn_single_warp = path.join(ot_dir, "{0}_{1}c.tif".format(basename, time.strftime("%Y%m%d%H%M%S")))
    nodata_value = -99 if IMAGE_FLOAT else 0
    gdalwarp(fn_single_warp, fn_single_trans,dest_nodata=nodata_value)

    if not DEV_FLAG:
        # Delete temporary file.
        remove(fn_single)
        remove(fn_single_trans)


#画像出力のために8bit範囲に変換する 標準偏差補正は外す
def exband2Range(src_matrix, min_value, max_value):
    """
    オンライン学習１　SAR画像解析基礎編
    
    画像の色調補正を行います
    
    関数   ： exband_histgram
    引数1  ： SARデータ2次元配列
    
    """
    # replace inf and nan with 0
    src_matrix = np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    #min_value = src_matrix.min()
    #max_value = src_matrix.max()
    #min_value = -94.0
    #max_value = 67
    print("min max-")
    print(src_matrix.min())
    print(src_matrix.max())
    if min_value < 0 :
        print("minval minus")
        print (min_value)
        
    min_result = 10
    max_result = 245

    # convert from min_result to max value
    grad = (max_result - min_result) / (max_value - min_value)
    intercept = min_result - min_value * grad
    src_matrix = src_matrix * grad + intercept
    
    # convert standard deviation
    #src_matrix = (src_matrix - src_matrix.mean()) / src_matrix.std() * 50 + src_matrix.mean()

    src_matrix[src_matrix < min_result] = min_result
    src_matrix[src_matrix > max_result] = max_result
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    if IMAGE_FLOAT:
        return src_matrix.astype(np.float32)
    else:
        return src_matrix.astype(np.uint8)

def exband2RangeMag(src_matrix, min_value, max_value, mag):
    """
    オンライン学習１　SAR画像解析基礎編
    
    画像の色調補正を行います
    
    関数   ： exband_histgram
    引数1  ： SARデータ2次元配列
    
    """
    # replace inf and nan with 0
    src_matrix = np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    #min_value = src_matrix.min()
    #max_value = src_matrix.max()
    #min_value = -94.0
    #max_value = 67
    print("min max-")
    print(src_matrix.min())
    print(src_matrix.max())
    if min_value < 0 :
        print("minval minus")
        print (min_value)
        
    min_result = 10
    max_result = 245

    # convert from min_result to max value
    grad = (max_result - min_result) / (max_value - min_value)
    intercept = min_result - min_value * grad
    src_matrix = src_matrix * grad + intercept
    
    src_matrix = src_matrix * mag
    # convert standard deviation
    #src_matrix = (src_matrix - src_matrix.mean()) / src_matrix.std() * 50 + src_matrix.mean()

    src_matrix[src_matrix < min_result] = min_result
    src_matrix[src_matrix > max_result] = max_result
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    if IMAGE_FLOAT:
        return src_matrix.astype(np.float32)
    else:
        return src_matrix.astype(np.uint8)

def exband2RangeShift(src_matrix, min_value, max_value, shift):
    """
    オンライン学習１　SAR画像解析基礎編
    
    画像の色調補正を行います
    
    関数   ： exband_histgram
    引数1  ： SARデータ2次元配列
    
    """
    # replace inf and nan with 0
    src_matrix = np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    #min_value = src_matrix.min()
    #max_value = src_matrix.max()
    #min_value = -94.0
    #max_value = 67
    print("min max-")
    print(src_matrix.min())
    print(src_matrix.max())
    if min_value < 0 :
        print("minval minus")
        print (min_value)
        
    min_result = 10
    max_result = 245

    # convert from min_result to max value
    grad = (max_result - min_result) / (max_value - min_value)
    intercept = min_result - min_value * grad
    src_matrix = src_matrix * grad + intercept
    
    #src_matrix = src_matrix * mag
    # convert standard deviation
    #src_matrix = (src_matrix - src_matrix.mean()) / src_matrix.std() * 50 + src_matrix.mean()

    src_matrix = src_matrix + shift

    src_matrix[src_matrix < min_result] = min_result
    src_matrix[src_matrix > max_result] = max_result
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    if IMAGE_FLOAT:
        return src_matrix.astype(np.float32)
    else:
        return src_matrix.astype(np.uint8)


def exband_histgram(src_matrix):
    """
    オンライン学習１　SAR画像解析基礎編
    
    画像の色調補正を行います
    
    関数   ： exband_histgram
    引数1  ： SARデータ2次元配列
    
    """
    # replace inf and nan with 0
    src_matrix = np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    min_value = src_matrix.min()
    max_value = src_matrix.max()
    #min_value = -94.0
    #max_value = 67
    print("min max-")
    print(min_value)
    print(max_value)
    if min_value < 0 :
        print("minval minus")
        print (min_value)
        
    min_result = 20
    max_result = 235

    # convert from min_result to max value
    grad = (max_result - min_result) / (max_value - min_value)
    intercept = min_result - min_value * grad
    src_matrix = src_matrix * grad + intercept
    
    # convert standard deviation
    #src_matrix = (src_matrix - src_matrix.mean()) / src_matrix.std() * 50 + src_matrix.mean()

    src_matrix[src_matrix < min_result] = min_result
    src_matrix[src_matrix > max_result] = max_result
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    if IMAGE_FLOAT:
        return src_matrix.astype(np.float32)
    else:
        return src_matrix.astype(np.uint8)


def logarithm_trans(src_matrix):
    """
    オンライン学習１　SAR画像解析基礎編
    
    SAR二次元データの強度をとります。
    
    関数   ： logarithm_trans
    引数1  ： SARデータ2次元配列
    
    返り値　: SARデータ2次元配列(強度)
    """
    return np.vectorize(lambda x: (log10(x) * 10 if x != 0 else -np.inf))((src_matrix * np.conjugate(src_matrix)).real)



if __name__ == "__main__":
    
    """
    オンライン学習１　SAR画像解析基礎編
    
    SARデータからSAR画像を作成するプログラムを実行します
    
    関数   ： create_comp_image
    引数1  ： SARデータ　HH偏波(*.mgp_HHm)
    引数2  ： SARデータ　HV偏波(*.mgp_HVm)
    引数3  ： SARデータ　VV偏波(*.mgp_VVm)
    引数4  ： SARデータ諸元ファイル(*.mgp_HHm_info)
    引数5  ： 出力ディレクトリ名
    引数6  ： マルチルックサイズ(ｱｼﾞマス方向)
    引数7  ： マルチルックサイズ(グランドレンジ方向)
    
    """
    """
    create_comp_image(r"",
                      r"",
                      r"",
                      r"",
                      r"",
                      , )
    """  
    """
    create_comp_image(r"/mnt/nfsdir/input/sar/Sendai01.mgp_HHm", 
                      r"/mnt/nfsdir/input/sar/Sendai01.mgp_HVm", 
                      r"/mnt/nfsdir/input/sar/Sendai01.mgp_VVm", 
                      r"/mnt/nfsdir/input/sar/Sendai01.mgp_HHm_info", 
                      r"/mnt/nfsdir/usr4/workspace/output/test", 10,10)                      
    """
    """
    create_comp_image(r"/mnt/nfsdir/input/sar/Obs15_aso-bridge.mgp_HHm", 
                      r"/mnt/nfsdir/input/sar/Obs15_aso-bridge.mgp_HVm", 
                      r"/mnt/nfsdir/input/sar/Obs15_aso-bridge.mgp_VVm", 
                      r"/mnt/nfsdir/input/sar/Obs15_aso-bridge.mgp_HHm_info", 
                      r"/mnt/nfsdir/usr4/workspace/output/4ref", 10,10)
  
    """
    create_comp_image(r"/mnt/nfsdir/input/sar/Obs09_aso-bridge.mgp_HHm", 
                      r"/mnt/nfsdir/input/sar/Obs09_aso-bridge.mgp_HVm", 
                      r"/mnt/nfsdir/input/sar/Obs09_aso-bridge.mgp_VVm", 
                      r"/mnt/nfsdir/input/sar/Obs09_aso-bridge.mgp_HHm_info", 
                      r"/mnt/nfsdir/usr4/workspace/output/G4U", 1,1)
    
    exit(0)

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
import argparse
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
    
    saveHistogram(path.join(ot_dir, "pdhist.txt"), pdhist)
    saveHistogram(path.join(ot_dir, "pvhist.txt"), pvhist)
    saveHistogram(path.join(ot_dir, "pshist.txt"), pshist)
  
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
    #exit(0)

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
    parser = argparse.ArgumentParser(description="create_comp_image")

    parser.add_argument("in_file_hh")
    parser.add_argument("in_file_hv")
    parser.add_argument("in_file_vv")
    parser.add_argument("in_file_info")
    parser.add_argument("out_path")
    parser.add_argument("filter_size_az", type=int)
    parser.add_argument("filter_size_gr", type=int)

    args = parser.parse_args()

    create_comp_image(args.in_file_hh,
                      args.in_file_hv,
                      args.in_file_vv,
                      args.in_file_info,
                      args.out_path,
                      args.filter_size_az,
                      args.filter_size_gr)
    
    exit(0)

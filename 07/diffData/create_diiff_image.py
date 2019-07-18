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

#HHHVVVそれぞれで差分を計算する

import numpy as np
from Common.mgp_info_reader import read_mgp_info, get_data, get_decimal_from_sexagesimal
from Common.gdal_command import gdaltranslate_gcp, gdalwarp
from scattering_matrix import create_scattering_matrix

from Common.constant import DEV_FLAG, DATA_PATH_BASE, IMAGE_FLOAT

from tifffile import imsave

from math import ceil, log10
from os import path, makedirs, remove
import time
import cv2
from ywanalysis import saveHistogram
import argparse

format_name = "GTiff"
mgp_key = "mgp_key"

def create_comp_image(in_hh, in_hv, in_vv, in_info, win_az, win_gr):
    """
    Create an image from raw SAR image data.
    :param in_hh: HH band data file of SAR image data
    :param in_hv: HV band data file of SAR image data
    :param in_vv: VV band data file of SAR image data
    :param in_info: SAR observation specification file
    :param win_az: Multilook size of AZ direction
    :param win_gr: Multilook size of GR direction
    """

    # Get actual file path
    in_hh = path.join(DATA_PATH_BASE, in_hh)
    in_hv = path.join(DATA_PATH_BASE, in_hv)
    in_vv = path.join(DATA_PATH_BASE, in_vv)
    in_info = path.join(DATA_PATH_BASE, in_info)

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
    
    返り値 : 複素数(実部：32bit,虚部：32bit)配列
    """
    print("band 1 read ...")
    hh = create_scattering_matrix(in_hh, n_az, n_gr, win_az, win_gr)
    print("band 2 read ...")
    hv = create_scattering_matrix(in_hv, n_az, n_gr, win_az, win_gr)
    print("band 3 read ...")
    vv = create_scattering_matrix(in_vv, n_az, n_gr, win_az, win_gr)

    loghh = logarithm_trans(hh)
    logvv = logarithm_trans(vv)
    loghv = logarithm_trans(hv)
    
    return loghh, logvv, loghv
    
def savetoTiff(hh, hv, vv, ofname, win_az, win_gr):
   # Logarithmic conversion and histogram adjustment
    matrix_r = visualize(hh, 8)#可視化のために●倍する
    matrix_g = visualize(hv, 8)
    matrix_b = visualize(vv, 8)

    n_az = int(get_data(mgp_key, "IMAGE_SIZE_AZ"))
    n_gr = int(get_data(mgp_key, "IMAGE_SIZE_GR"))
    n_img_az = ceil(n_az / win_az)
    n_img_gr = ceil(n_gr / win_gr)

    # Create Tiff image file.
    """
    SAR二次元データを画像として出力します
    
    関数  : imsave
    引数1 : 出力ファイル名(*.tif)
    引数2 : SAR二次元データ
        RGB画像の場合にはnp.stack([R成分、G成分、B成分])
    """
    print("imsave start")
    
    dirname, basename = path.split(ofname)
    fn_single = path.join(dirname, "tmp_base_{0}.tif".format(time.strftime("%Y%m%d%H%M%S")))
    fn_single_trans = path.join(dirname, "tmp_trans_{0}.tif".format(time.strftime("%Y%m%d%H%M%S")))
    imsave(fn_single, np.stack([matrix_r, matrix_g, matrix_b]))
    
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
    nodata_value = -99 if IMAGE_FLOAT else 0
    gdalwarp(ofname, fn_single_trans,dest_nodata=nodata_value)

    if not DEV_FLAG:
        # Delete temporary file.
        remove(fn_single)
        remove(fn_single_trans)
        
    print("imsave end")

def visualize(src_matrix, mag):
    """
    オンライン学習１　SAR画像解析基礎編
    
    画像の色調補正を行います
    
    関数   : exband_histgram
    引数1  : SARデータ2次元配列(強度)
    
    返り値　: ヒストグラム調整のされたSARデータ2次元配列(強度)
    """
    # replace inf and nan with 0
    #src_matrix = np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)
    src_matrix = src_matrix * mag
    
    min_result = 0
    max_result = 250
    src_matrix[src_matrix < min_result] = min_result
    src_matrix[src_matrix > max_result] = max_result

    if IMAGE_FLOAT:
        return src_matrix.astype(np.float32)
    else:
        return src_matrix.astype(np.uint8)


def exband_histgram(src_matrix):
    """
    オンライン学習１　SAR画像解析基礎編
    
    画像の色調補正を行います
    
    関数   : exband_histgram
    引数1  : SARデータ2次元配列(強度)
    
    返り値　: ヒストグラム調整のされたSARデータ2次元配列(強度)
    """
    # replace inf and nan with 0
    src_matrix = np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    min_value = src_matrix.min()
    max_value = src_matrix.max()
    min_result = 20
    max_result = 235

    # convert from min_result to max value
    grad = (max_result - min_result) / (max_value - min_value)
    intercept = min_result - min_value * grad
    src_matrix = src_matrix * grad + intercept
    
    # convert standard deviation
    src_matrix = (src_matrix - src_matrix.mean()) / src_matrix.std() * 50 + src_matrix.mean()

    src_matrix[src_matrix < min_result] = min_result
    src_matrix[src_matrix > max_result] = max_result
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    if IMAGE_FLOAT:
        return src_matrix.astype(np.float32)
    else:
        return src_matrix.astype(np.uint8)

def median_filter(src, ksize):
    # 畳み込み演算をしない領域の幅
    d = int((ksize-1)/2)
    h, w = src.shape[0], src.shape[1]
    
    # 出力画像用の配列（要素は入力画像と同じ）
    dst = src.copy()

    for y in range(d, h - d):
        for x in range(d, w - d):
            # 近傍にある画素値の中央値を出力画像の画素値に設定
            dst[y][x] = np.median(src[y-d:y+d+1, x-d:x+d+1])

    return dst


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
    
    関数   ： create_comp_imageDB
    引数1  ： SARデータ　HH偏波(*.mgp_HHm)
    引数2  ： SARデータ　HV偏波(*.mgp_HVm)
    引数3  ： SARデータ　VV偏波(*.mgp_VVm)
    引数4  ： SARデータ諸元ファイル(*.mgp_HHm_info)
    引数5  ： 出力ディレクトリ名
    引数6  ： マルチルックサイズ(ｱｼﾞマス方向)
    引数7  ： マルチルックサイズ(グランドレンジ方向)
    """
    
    parser = argparse.ArgumentParser(description="create_comp_image")
    parser.add_argument("in_file1_hh")
    parser.add_argument("in_file1_hv")
    parser.add_argument("in_file1_vv")
    parser.add_argument("in_file1_info")
    parser.add_argument("in_file2_hh")
    parser.add_argument("in_file2_hv")
    parser.add_argument("in_file2_vv")
    parser.add_argument("in_file2_info")
    parser.add_argument("out_path")
    parser.add_argument("filter_size_az", type=int)
    parser.add_argument("filter_size_gr", type=int)
    
    args = parser.parse_args()

    ot_dir = path.abspath(path.join(DATA_PATH_BASE, args.out_path))
    makedirs(ot_dir, exist_ok=True)

    filename = path.splitext(path.basename( args.in_file1_hh))[0]
    if filename.lower().startswith("sendai"):
        basename = "Sendai"
    elif filename.lower().startswith("obs15"):
        basename = "Kumamoto"
    elif filename.lower().startswith("obs09"):
        basename = "Kumamoto"
    else:
        basename = filename

    loghh0, logvv0, loghv0 = create_comp_image(
                        args.in_file1_hh,
                        args.in_file1_hv,
                        args.in_file1_vv,
                        args.in_file1_info,
                        args.filter_size_az,
                        args.filter_size_gr)
                        
    print("load data end")
    
    loghh1, logvv1, loghv1 = create_comp_image(
                        args.in_file2_hh,
                        args.in_file2_hv,
                        args.in_file2_vv,
                        args.in_file2_info,
                        args.filter_size_az,
                        args.filter_size_gr)
    print("load data end")

    print (loghh0.dtype)
    print (loghh0.shape)
    
    loghh0 = median_filter(loghh0, 5)
    loghv0 = median_filter(loghv0, 5)
    logvv0 = median_filter(logvv0, 5)
    loghh1 = median_filter(loghh1, 5)
    loghv1 = median_filter(loghv1, 5)
    logvv1 = median_filter(logvv1, 5)

    savetoTiff(loghh0, loghv0, logvv0, path.join(ot_dir, "{0}0.tif".format(basename)), args.filter_size_az, args.filter_size_gr)
    savetoTiff(loghh1, loghv1, logvv1, path.join(ot_dir, "{0}0.tif".format(basename)), args.filter_size_az, args.filter_size_gr)

    hhdiff = np.abs(loghh0 - loghh1)
    vvdiff = np.abs(logvv0 - logvv1)
    hvdiff = np.abs(loghv0 - loghv1)
    
    #oHHhist = np.histogram(hhdiff, 240, (0, 120))
    #oHVhist = np.histogram(hvdiff, 240, (0, 120))
    #oVVhist = np.histogram(vvdiff, 240, (0, 120))
    
    #dirPath = '/mnt/nfsdir/usr4/workspace/result.mine/histogram/'
    #saveHistogram(dirPath + "dhhhist.txt", oHHhist)
    #saveHistogram(dirPath + "dhvhist.txt", oHVhist)
    #saveHistogram(dirPath + "dvvhist.txt", oVVhist)
    
    fn_diff = path.join(ot_dir, "{0}_diff.tif".format(basename))
    savetoTiff(hhdiff, hvdiff, vvdiff, fn_diff, args.filter_size_az, args.filter_size_gr)
    #savetoTiff(hhdiff, hhdiff, hhdiff, r"/mnt/nfsdir/usr4/workspace/result.mine/diffHHout.tif")
    #savetoTiff(hvdiff, hvdiff, hvdiff, r"/mnt/nfsdir/usr4/workspace/result.mine/diffHVout.tif")
    #savetoTiff(vvdiff, vvdiff, vvdiff, r"/mnt/nfsdir/usr4/workspace/result.mine/diffVVout.tif")
    
    exit(0)

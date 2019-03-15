# coding: utf-8

# Copyright (c) 2019 National Institute of Information and Communications Technology
# Released under the GPLv2 license

import numpy as np
from Common.mgp_info_reader import read_mgp_info, get_data, get_decimal_from_sexagesimal
from Common.gdal_command import gdaltranslate_gcp, gdalwarp
from scattering_matrix import create_scattering_matrix

from Common.constant import DEV_FLAG, DATA_PATH_BASE, IMAGE_FLOAT

from tifffile import imsave

from math import ceil, log10
from os import path, makedirs, remove
import time


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

    fn_single = path.join(ot_dir, "tmp_{0}_base.tif".format(basename))
    fn_single_trans = path.join(ot_dir, "tmp_{0}_trans.tif".format(basename))

    read_mgp_info(mgp_key, in_info)
    
    n_az = int(get_data(mgp_key, "IMAGE_SIZE_AZ"))
    n_gr = int(get_data(mgp_key, "IMAGE_SIZE_GR"))
    n_img_az = ceil(n_az / win_az)
    n_img_gr = ceil(n_gr / win_gr)

    # Read raw SAR image data file.
    
    """
    オンライン学習１　SAR画像解析基礎編
    SARデータの読み込み
    
    SARデータを読み込み、ﾏﾙﾁﾙｯｸを行った結果を複素数で出力します
    
    関数  : create_scattering_matrix
    引数1 : 入力ファイル(*.mgp_HHm　or *.mgp_HVm or *.mgp_VVm)
    引数2 : 出力2次元行列(実部)
    引数3 : 出力2次元行列(虚部)
    引数4 : SARデータ画像サイズ(アジマス方向)
    引数5 : SARデータ画像サイズ(グランドレンジ方向)
    引数6 : ﾏﾙﾁﾙｯｸサイズ(アジマス方向)
    引数7 : ﾏﾙﾁﾙｯｸサイズ(グランドレンジ方向)
    
    返り値 : numpy complex64(複素数(実部：32bit,虚部：32bit))配列
    """
    print("band 1 read ...")
    hh = create_scattering_matrix(in_hh, n_az, n_gr, win_az, win_gr)
    print("band 2 read ...")
    hv = create_scattering_matrix(in_hv, n_az, n_gr, win_az, win_gr)
    print("band 3 read ...")
    vv = create_scattering_matrix(in_vv, n_az, n_gr, win_az, win_gr)

    # Logarithmic conversion and histogram adjustment
    matrix_r = exband_histgram(logarithm_trans(hh))
    matrix_g = exband_histgram(logarithm_trans(hv))
    matrix_b = exband_histgram(logarithm_trans(vv))

    # Create Tiff image file.
    """
    オンライン学習１　SAR画像解析基礎編
    画像の保存
    
    読み込んだSARデータを格納した二次元配列を画像(.tif)として出力します
    
    引数1  ： 出力ファイル名(*.tif)
    引数2  : SARデータ2次元行列
                - RGB合成画像を生成する場合にはnp.stack([R要素,G要素,B要素])
    """
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
    fn_single_warp = path.join(ot_dir, "{0}_{1}c.tif".format(basename, time.strftime("%Y%m%d%H%M%S")))
    nodata_value = -99 if IMAGE_FLOAT else 0
    gdalwarp(fn_single_warp, fn_single_trans,dest_nodata=nodata_value)

    if not DEV_FLAG:
        # Delete temporary file.
        remove(fn_single)
        remove(fn_single_trans)


def exband_histgram(src_matrix):
    """
    オンライン学習１　SAR画像解析基礎編
    ヒストグラムの調整
    
    SAR画像の色調補正を行います
    
    引数1  ： SARデータ2次元配列
    
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


def logarithm_trans(src_matrix):
    """
    Logarithmic convert complex matrix
    :param src_matrix: Numpy array of raw SAR image data
    :return: converted data
    """
    return np.vectorize(lambda x: (log10(x) * 10 if x != 0 else -np.inf))(np.abs(src_matrix))



if __name__ == "__main__":
    
    """
    オンライン学習１　SAR画像解析基礎編
    プログラムの実行
    
    SARデータからSAR画像を作成するプログラムを実行します
    
    引数1  ： SARデータ　HH偏波(*.mgp_HHm)
    引数2  ： SARデータ　HV偏波(*.mgp_HVm)
    引数3  ： SARデータ　VV偏波(*.mgp_VVm)
    引数4  ： SARデータ諸元ファイル(*.mgp_HHm_info)
    引数5  ： 出力ディレクトリ名
    引数6  ： マルチルックサイズ(ｱｼﾞマス方向)
    引数7  ： マルチルックサイズ(グランドレンジ方向)
    
    """
    create_comp_image(r"/mnt/nfsdir/input/Obs15_aso-bridge.mgp_HHm",
                      r"/mnt/nfsdir/input/Obs15_aso-bridge.mgp_HVm",
                      r"/mnt/nfsdir/input/Obs15_aso-bridge.mgp_VVm",
                      r"/mnt/nfsdir/input/Obs15_aso-bridge.mgp_HHm_info",
                      r"output/test",
                      10, 10)
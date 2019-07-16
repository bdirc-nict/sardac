# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: extract_land_slide_area.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and Communications Technology
#==================================================================================

import numpy as np
from tifffile import imread, imsave
from os import makedirs, path, remove
from Common.tif_util import create_res5m_tiff, get_threshold, trans_geotiff, create_binary_array,RectGeoTiffCoordinateCalculator, average_filter

from Common.constant import DEV_FLAG, DATA_PATH_BASE

import time
import argparse


def extract_land_slide_area(in_file1, in_file2, ot_dir, threshold, filter_size_az, filter_size_gr):
    
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    SAR画像から土砂崩れ領域を抽出します
    
    関数   ： extract_land_slide_area
    引数1  ： SAR画像(災害前)
    引数2  ： SAR画像(災害後)
    引数3  ： 出力ディレクトリ名
    引数4  ： 閾値("0"：自動で閾値を決定、"0以外[0 255]"：指定した値が閾値)
    引数5  ： 平均化サイズ(Az方向)
    引数6  ： 平均化サイズ(Gr方向)
    
    """
    
    # Get destination file name
    filename = path.splitext(path.basename(in_file1))[0]
    if filename.lower().startswith("sendai"):
        basename = "Sendai"
    elif filename.lower().startswith("kumamoto"):
        basename = "Kumamoto"
    else:
        basename = filename
    
    # Get actual file path
    in_file1 = path.join(DATA_PATH_BASE, in_file1)
    in_file2 = path.join(DATA_PATH_BASE, in_file2)
    ot_dir = path.join(DATA_PATH_BASE, ot_dir)
    makedirs(ot_dir, exist_ok=True)

    # Get the area to output
    info1 = RectGeoTiffCoordinateCalculator(in_file1)
    ul1 = info1.get_upper_left()
    lr1 = info1.get_lower_right()
    info2 = RectGeoTiffCoordinateCalculator(in_file2)
    ul2 = info2.get_upper_left()
    lr2 = info2.get_lower_right()

    ul = (max(ul1[0],ul2[0]), min(ul1[1],ul2[1]))
    lr = (min(lr1[0],lr2[0]), max(lr1[1],lr2[1]))

    out_area = (ul[0],ul[1],lr[0],lr[1])

    # Create Geotiff with 5m Resolution.
    fn_trans_1 = path.join(ot_dir, "tmp_5m_1.tif")
    create_res5m_tiff(in_file1, fn_trans_1, out_area)
    fn_trans_2 = path.join(ot_dir, "tmp_5m_2.tif")
    create_res5m_tiff(in_file2, fn_trans_2, out_area)

    # Load images before and after landslide 
    img1 = imread(fn_trans_1)
    img2 = imread(fn_trans_2)
    
    # Calculate differences of images before and after landslide
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    災害前後SAR画像から差分画像を生成します
    
    """
    img = np.abs(img1.astype(dtype=np.int16) - img2.astype(dtype=np.int16)).astype(dtype=np.uint8)
    imsave(path.join(ot_dir, "tmp_sub.tif"), img)
    
    # Apply averaging filter to difference image
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    差分画像に平均化処理を行うプログラムを実行します
    
    関数   ： average_filter
    引数1  ： SAR二次元データ（単バンド）
    引数2  ： 平均化サイズ(Az方向)
    引数2  ： 平均化サイズ(Gr方向)
    
    """
    img = average_filter(img, filter_size_az, filter_size_gr)
    imsave(path.join(ot_dir, "tmp_sub_avg.tif"), img)


    # Calculated from data if no threshold is specified.
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    差分画像の各バンド毎に閾値を算出するプログラムを実行します
    
    関数   ： get_threshold
    引数1  ： SAR二次元データ（単バンド）
    引数2  ： Nodata値
    
    """
    threshold_rgb = [threshold, threshold, threshold]
    
    if threshold == 0:
        threshold_rgb[0] = get_threshold(img[:, :, 0], 0)
        threshold_rgb[1] = get_threshold(img[:, :, 1], 0)
        threshold_rgb[2] = get_threshold(img[:, :, 2], 0)

   
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    差分画像から各バンド毎に二値(255：被災領域、0：非被災領域)画像を生成し、
    
    関数   ： create_binary_array
    引数1  ： SAR二次元データ(単バンド)
    引数2  ： 閾値[0 255]
    引数3　： 被災領域値
    引数4　： 非被災領域値
    
    いずれの閾値よりも値の大きい(変動の大きい)領域を抽出し、
    二値化画像を生成します
    
    bin_all[(bin0==255) & (bin1==255) & (bin2==255)] = 255：
    各バンド毎に生成した二値画像のピクセル値がすべて255の場合に、土砂崩れ領域として抽出
    
    """
     # Create binarized data.
    bin0 = create_binary_array(img[:, :, 0], threshold_rgb[0], small_value=0, large_value=255)
    bin1 = create_binary_array(img[:, :, 1], threshold_rgb[1], small_value=0, large_value=255)
    bin2 = create_binary_array(img[:, :, 2], threshold_rgb[2], small_value=0, large_value=255)

    bin_all = np.zeros(bin0.shape,dtype=np.uint8)
    bin_all[(bin0==255) & (bin1==255) & (bin2==255)] = 255
    fn_bin = path.join(ot_dir, "tmp_bin_tmp_and.tif")
    imsave(fn_bin, bin_all)

    # Create Geotiff from binarized data.
    fn_bin_trans = path.join(ot_dir, "{0}_{1}cb.tif".format(basename, time.strftime("%Y%m%d%H%M%S")))
    trans_geotiff(fn_bin_trans, bin_all, fn_trans_1)

    if not DEV_FLAG:
        # Delete temporary file.
        remove(fn_trans_1)
        remove(fn_trans_2)
        remove(path.join(ot_dir, "tmp_sub.tif"))
        remove(path.join(ot_dir, "tmp_sub_avg.tif"))
        remove(fn_bin)


if __name__ == "__main__":
    
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    SAR画像から土砂崩れ領域を抽出するプログラムを実行します
    
    関数   ： extract_flooded_area
    引数1  ： SAR画像
    引数2  ： 出力ディレクトリ名
    
    """
    parser = argparse.ArgumentParser(description="extract_land_slide_area")

    parser.add_argument("in_file_before")
    parser.add_argument("in_file_after")
    parser.add_argument("out_path")
    parser.add_argument("--threshold", "-t", default=0, type=int)
    parser.add_argument("--filter_size", "-s", nargs=2, default=[1,1], type=int)

    args = parser.parse_args()

    extract_land_slide_area(args.in_file_before,
                            args.in_file_after,
                            args.out_path,
                            threshold=args.threshold,
                            filter_size_az=args.filter_size[0],
                            filter_size_gr=args.filter_size[1])

    exit(0)
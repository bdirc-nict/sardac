# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: extract_flooded_area.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and Communications Technology
#==================================================================================

from tifffile import imread, imsave
from os import makedirs, path, remove
from Common.tif_util import create_res5m_tiff, get_threshold, create_binary_array, trans_geotiff, average_filter

from Common.constant import DEV_FLAG, DATA_PATH_BASE
import time
import argparse


def extract_flooded_area(in_file, ot_dir, threshold,filter_size_az, filter_size_gr):
    
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    SAR画像から浸水領域を抽出します
    
    関数   ： extract_flooded_area
    引数1  ： SAR画像
    引数2  ： 出力ディレクトリ名
    引数3  ： 閾値("0"：自動で閾値を決定、"0以外[0 255]"：指定した値が閾値)
    引数4  ： 平均化サイズ(Az方向)
    引数5  ： 平均化サイズ(Gr方向)
    
    """
    
    # Get destination file name
    filename = path.splitext(path.basename(in_file))[0]
    if filename.lower().startswith("sendai"):
        basename = "Sendai"
    elif filename.lower().startswith("kumamoto"):
        basename = "Kumamoto"
    else:
        basename = filename
    
    
    # Get actual file path
    in_file = path.join(DATA_PATH_BASE, in_file)
    ot_dir = path.join(DATA_PATH_BASE, ot_dir)
    makedirs(ot_dir, exist_ok=True)

    # Create Geotiff with 5m Resolution.
    fn_trans = path.join(ot_dir, "tmp_5m.tif")
    create_res5m_tiff(in_file, fn_trans)

    # Take out only the blue band.
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    抽出対象画像(単色)の選定を行います
    
    """
    img = imread(fn_trans)
    img = average_filter(img[:, :, 2], filter_size_az, filter_size_gr)

    # Calculated from data if no threshold is specified.
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    浸水領域を抽出する閾値を自動で算出するプログラムを実行します
    
    関数   ： get_threshold
    引数1  ： SAR画像
    引数2  ： Nodata値
    
    """
    if threshold == 0:
        threshold = get_threshold(img, 0)

    # Create binarized data.
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    浸水領域の二値(255：浸水領域、0：非浸水領域)画像を生成するプログラムを実行します
    
    関数   ： create_binary_array
    引数1  ： SAR画像
    引数2  ： 閾値
    引数3　： 浸水領域値
    引数4　： 非浸水領域値
    
    """
    img_bin = create_binary_array(img, threshold, small_value=255, large_value=0)
    fn_bin = path.join(ot_dir, "tmp_bin_tmp.tif")
    imsave(fn_bin, img_bin)

    # Create Geotiff from binarized data.
    fn_bin_trans = path.join(ot_dir, "{0}_{1}cb.tif".format(basename, time.strftime("%Y%m%d%H%M%S")))
    trans_geotiff(fn_bin_trans, img_bin, fn_trans)

    if not DEV_FLAG:
        # Delete temporary file.
        remove(fn_trans)
        remove(fn_bin)



if __name__ == "__main__":
    
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    SAR画像から浸水領域を抽出するプログラムを実行します
    
    関数   ： extract_flooded_area
    引数1  ： SAR画像
    引数2  ： 出力ディレクトリ名
    
    """
    parser = argparse.ArgumentParser(description="extract_flooded_area")

    parser.add_argument("in_file")
    parser.add_argument("out_path")
    parser.add_argument("--threshold", "-t", default=0, type=int)
    parser.add_argument("--filter_size", "-s", nargs=2, default=[1,1], type=int)

    args = parser.parse_args()

    extract_flooded_area(args.in_file,
                         args.out_path,
                         threshold=args.threshold,
                         filter_size_az=args.filter_size[0],
                         filter_size_gr=args.filter_size[1])

    exit(0)

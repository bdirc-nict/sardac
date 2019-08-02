# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: trans_vector.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and Communications Technology
#==================================================================================

from Common.tif_util import RectGeoTiffCoordinateCalculator
from add_height_vector import add_height_vector

from Common.constant import DEV_FLAG, DATA_PATH_BASE
from Common.mgp_info_reader import read_mgp_info, get_data

from tifffile import imread
from shapefile import Writer as ShpWriter
from shapefile import POLYGON

from os import path, makedirs, remove
import itertools
import time
import argparse


def trans_vector(in_file, ot_dir, output_flg, dem_path, flood_flg, info_list):
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換

    二値画像からポリゴンを生成します
    
    関数   ： trans_vector
    引数1  ： 入力ファイル名(.tif)
    引数2  ： 出力ディレクトリ名
    引数3　： 出力フラグ(0：被災領域、1：非被災領域)
    引数4　： 数値標高ﾓﾃﾞﾙ名(.shp)
    引数5　： 災害フラグ(True：浸水、False：土砂崩れ)

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
    dem_path = path.join(DATA_PATH_BASE, dem_path)
    makedirs(ot_dir, exist_ok=True)

    print("creating shapefile ...")

    # Create shapefile information of output area
    
    fn_tmp = path.join(ot_dir, "tmp.shp")
    writer = ShpWriter(target=fn_tmp, shapeType=POLYGON)
    writer.field("id", "C", "20", 0)
    writer.field("type", "C", "10", 0)
    writer.field("format", "C", "10", 0)
    writer.field("dis_tf", "C", "8", 0)
    writer.field("dis_tt", "C", "8", 0)
    writer.field("proc", "C", "8", 0)
    writer.field("pre_dn", "C", "10", 0)
    writer.field("pre_st", "C", "10", 0)
    writer.field("post_dn", "C", "10", 0)
    writer.field("post_st", "C", "10", 0)
    
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    ポリゴンに付与する属性情報を定義するプログラムを実行します
    
    関数   ： get_flood_record
    関数   ： get_land_slide_record

    """
    pre_dn = ""
    pre_st = ""
    post_dn = ""
    post_st = ""
    if len(info_list) == 1:
        read_mgp_info("info1", info_list[0])
        vals = get_data("info1", "SCENE_START_TIME").split("/")
        post_st = vals[0]+vals[1]+vals[2]
        post_dn = path.splitext(path.basename(info_list[0]))[0]
    elif len(info_list) == 2:
        read_mgp_info("info1", info_list[0])
        read_mgp_info("info2", info_list[1])
        vals = get_data("info1", "SCENE_START_TIME").split("/")
        pre_st = vals[0]+vals[1]+vals[2]
        pre_dn = path.splitext(path.basename(info_list[0]))[0]
        vals = get_data("info2", "SCENE_START_TIME").split("/")
        post_st = vals[0]+vals[1]+vals[2]
        post_dn = path.splitext(path.basename(info_list[1]))[0]

    if flood_flg:
        # flood processing
        record = get_flood_record(pre_dn, pre_st, post_dn, post_st)
    else:
        # landslide processing
        record = get_land_slide_record(pre_dn, pre_st, post_dn, post_st)
        
        
    # Read binary image and get coordinate information
    bin = imread(in_file)
    rect_tiff = RectGeoTiffCoordinateCalculator(in_file)


    # Create rectangle polygon of output area and output to shapefile
    n_shape = bin.shape[0] * bin.shape[1]
    cnt = 0
    for x_index, y_index in itertools.product(range(bin.shape[1]), range(bin.shape[0])):
        
        """
        オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
        二値画像の各ピクセル四隅座標(緯度、経度)を計算するプログラムを実行します
        
        関数   ： create_polygon_points
        引数1  ： 対象ピクセルのx番号
        引数2  ： 対象ピクセルのy番号
        引数3　： 二値画像の図形情報(ファイル名、画像サイズ等)を持つインスタンス
    
        """
        points = create_polygon_points(x_index, y_index, rect_tiff)
        
        """
        オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
        二値画像からメッシュを作成します
        
        bin[y_index, x_index] == 255)：ピクセル値が255の場合
        output_flg == "0"：被災領域のメッシュを作成
        output_flg == "1"：非被災領域のメッシュを作成
    
        """
        if (bin[y_index, x_index] == 255) == (output_flg == "0"):
            # This pixel is output target.
            writer.poly([points])
            writer.record(*record)

        cnt = cnt + 1
        if cnt % 100000 == 0:
            print("{0}K / {1}K".format(cnt/1000, n_shape/1000))
    writer.close()
    print("created shapefile .")

    if output_flg == "0":
        fn_out = path.join(ot_dir, "{0}_{1}cbp.shp".format(basename, time.strftime("%Y%m%d%H%M%S")))
    else:
        fn_out = path.join(ot_dir, "{0}_{1}cbpr.shp".format(basename, time.strftime("%Y%m%d%H%M%S")))

    # Attach elevation value
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換

    メッシュデータに標高値を付与するプログラムを実行します
    
    関数   ： add_height_vector
    引数1  ： 入力メッシュデータ名(.tif)
    引数2  ： 数値標高ﾓﾃﾞﾙ名(.shp)
    引数3　： 出力ファイル名(.shp)

    """
    add_height_vector([fn_tmp], dem_path, fn_out)

    if not DEV_FLAG:
        # Delete temporary file.
        remove("{0}.shp".format(path.splitext(fn_tmp)[0]))
        remove("{0}.shx".format(path.splitext(fn_tmp)[0]))
        remove("{0}.dbf".format(path.splitext(fn_tmp)[0]))


def create_polygon_points(x_index, y_index, recttiff):
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    二値画像の各ピクセル四隅座標(緯度、経度)を計算します
    
    関数   ： create_polygon_points
    引数1  ： 対象ピクセルのx番号
    引数2  ： 対象ピクセルのy番号
    引数3　： 二値画像の図形情報(ファイル名、画像サイズ等)を持つインスタンス
    返り値 ： 対象ピクセルの四隅座標(緯度、経度)
    
    """
    lon1 = recttiff.get_lon_on_pixel_index(x_index)
    lon2 = recttiff.get_lon_on_pixel_index(x_index+1)
    lat1 = recttiff.get_lat_on_pixel_index(y_index)
    lat2 = recttiff.get_lat_on_pixel_index(y_index+1)
    return [(lon1,lat1), (lon1,lat2), (lon2,lat2), (lon2,lat1), (lon1,lat1)]

def get_flood_record(pre_dn, pre_st, post_dn, post_dt):
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    浸水領域ポリゴンに付与する属性情報を定義します
    
    関数   ： get_flood_record
    返り値 ： 浸水領域属性情報

    """
    atime = time.strftime("%Y%m%d%H%M%S")
    dbf_id = "{0}_210".format(atime)
    dbf_format = ""
    dbf_dis_tf = ""
    dbf_dis_tt = ""
    dbf_proc = time.strftime("%Y%m%d")
    dbf_type = "flood"
    dbf_pre_dn = pre_dn
    dbf_pre_st = pre_st
    dbf_post_dn = post_dn
    dbf_post_st = post_dt

    return [dbf_id, dbf_type, dbf_format, dbf_dis_tf, dbf_dis_tt, dbf_proc, dbf_pre_dn, dbf_pre_st, dbf_post_dn, dbf_post_st]


def get_land_slide_record(pre_dn, pre_st, post_dn, post_dt):
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換
    
    土砂崩れ領域ポリゴンに付与する属性情報を定義します
    
    関数   ： get_land_slide_record
    返り値 ： 土砂崩れ領域属性情報

    """
    atime = time.strftime("%Y%m%d%H%M%S")
    dbf_id = "{0}_110".format(atime)
    dbf_format = ""
    dbf_dis_tf = ""
    dbf_dis_tt = ""
    dbf_proc = time.strftime("%Y%m%d")
    dbf_type = "landslide"
    dbf_pre_dn = pre_dn
    dbf_pre_st = pre_st
    dbf_post_dn = post_dn
    dbf_post_st = post_dt

    return [dbf_id, dbf_type, dbf_format, dbf_dis_tf, dbf_dis_tt, dbf_proc, dbf_pre_dn, dbf_pre_st, dbf_post_dn, dbf_post_st]


if __name__ == "__main__":
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換

    二値画像からポリゴンを生成するプログラムを実行します
    
    関数   ： trans_vector
    引数1  ： 入力ファイル名(.tif)
    引数2  ： 出力ディレクトリ名
    引数3　： 出力フラグ(0：被災領域、1：非被災領域)
    引数4　： 数値標高ﾓﾃﾞﾙ名(.shp)
    引数5　： 災害フラグ(True：浸水、False：土砂崩れ)

    """
    parser = argparse.ArgumentParser(description="trans_vector")

    parser.add_argument("in_file")
    parser.add_argument("out_path")
    parser.add_argument("dem_file")
    parser.add_argument("type", choices=["flood", "landslide"])
    parser.add_argument("--non_damaged", action="store_true")
    parser.add_argument("--info_path", nargs="*")
    args = parser.parse_args()

    if args.type is None or (args.type == "landslide" and len(args.info_path) != 2) or (args.type == "flood" and len(args.info_path) not in (1,2)):
        print("infoファイルの数が正しくありません")
        exit(1)

    trans_vector(args.in_file,
                 args.out_path,
                 "1" if args.non_damaged else "0",
                 args.dem_file,
                 args.type == "flood",
                 args.info_path)

    exit(0)

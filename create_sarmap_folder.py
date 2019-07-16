# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: create_sarmap_folder.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

from Common.input_txt_writer import InputTxtData

from os import path, makedirs, listdir
from shutil import copy2, rmtree
import time
import argparse

def create_sarmap_folder(data_type_flg, ot_dir, *src_lists):
    
    """
    SAR分析チャレンジ ハンズオン

    被災領域のラスタ・ベクタデータを登録するためのフォルダを構成します
    
    関数：create_sarmap_folder
    引数1：土砂崩れ(1)、浸水(2)
    引数2：出力ディレクトリ名
    引数3：入力ラスタ・ベクタデータ群
    """

    if data_type_flg == 1:
        # landslide area
        time_str = time.strftime("%Y%m%d%H%M%S")
        """
        SAR分析チャレンジ ハンズオン
        
        土砂崩れ領域のラスタ・ベクタデータの情報を定義するプログラムを実行します
        
        関数：create_land_slide_data
        引数1：データのID
        引数2：ラスタ・ベクタデータの種類
        
            4: "単偏波合成画像（災害前）",
            5: "単偏波合成画像（災害後）",
            6: "Covariance画像（災害前）",
            7: "Covariance画像（災害後）",
            8: "四成分合成画像（災害前）",
            9: "四成分合成画像（災害後）",
            10: "オリジナル画像1（災害前）",
            11: "オリジナル画像1（災害後）",
            12: "オリジナル画像2（災害前）",
            13: "オリジナル画像2（災害後）",
            14: "オリジナル画像3（災害前）",
            15: "オリジナル画像3（災害後）",
            16: "オリジナル画像4（災害前）",
            17: "オリジナル画像4（災害後）",
            18: "オリジナル画像5（災害前）",
            19: "オリジナル画像5（災害後）",
            20: "領域抽出ファイル",
            21: "差分画像"
            
        引数3：観測日時
        
            災害前：20151205で固定
            災害後：20160417で固定
            差分画像(二値画像)、差分ポリゴンShapeFile(土砂崩れマップ)は20160417で固定
            
        """
        input_data_list = [
            InputTxtData.create_land_slide_data(time_str, 4, "20151205"),
            InputTxtData.create_land_slide_data(time_str, 5, "20160417"),
            InputTxtData.create_land_slide_data(time_str, 21, "20160417"),
            InputTxtData.create_land_slide_data(time_str, 20, "20160417")
        ]

    elif data_type_flg == 2:
        # flooded area
        time_str = time.strftime("%Y%m%d%H%M%S")
        
        """
        SAR分析チャレンジ ハンズオン
        
        浸水領域のラスタ・ベクタデータの情報を定義するプログラムを実行します
        
        関数：create_flood_data
        引数1：データのID
        引数2：ラスタ・ベクタデータの種類
        
            4: "単偏波合成画像（災害前）",
            5: "単偏波合成画像（災害後）",
            6: "Covariance画像（災害前）",
            7: "Covariance画像（災害後）",
            8: "四成分合成画像（災害前）",
            9: "四成分合成画像（災害後）",
            10: "オリジナル画像1（災害前）",
            11: "オリジナル画像1（災害後）",
            12: "オリジナル画像2（災害前）",
            13: "オリジナル画像2（災害後）",
            14: "オリジナル画像3（災害前）",
            15: "オリジナル画像3（災害後）",
            16: "オリジナル画像4（災害前）",
            17: "オリジナル画像4（災害後）",
            18: "オリジナル画像5（災害前）",
            19: "オリジナル画像5（災害後）",
            20: "領域抽出ファイル",
            21: "差分画像"
        """
        input_data_list = [
            InputTxtData.create_flood_data(time_str, 5),
            InputTxtData.create_flood_data(time_str, 21),
            InputTxtData.create_flood_data(time_str, 20)
        ]

    if path.exists(ot_dir) and len(listdir(ot_dir)) > 0:
        print("出力先\"{0}\"が空ではありません。続行すると中のファイルはすべて削除されます。続行しますか？".format(ot_dir))

        while True:
            get = input("[y/n]")
            if get == "n":
                return
            if get == "y":
                break
        rmtree(ot_dir)
        makedirs(ot_dir)

    for i, input_data in zip(range(len(input_data_list)), input_data_list):
        src_list = src_lists[i] if len(src_lists) > i else []

        target_path = path.join(ot_dir, "{0:02}".format(i+1))
        makedirs(target_path)
        for file in src_list:
            copy2(file, target_path)
            if path.splitext(file)[1] == ".shp":
                dbf_path = path.splitext(file)[0] + ".dbf"
                shx_path = path.splitext(file)[0] + ".shx"
                copy2(dbf_path, target_path)
                copy2(shx_path, target_path)

        input_data.write_file(target_path)


if __name__ == "__main__":
    
    """
    SAR分析チャレンジ ハンズオン

    浸水領域のラスタ・ベクタデータを登録するためのフォルダを構成するプログラムを実行します
    
    file_list_1：仙台SAR画像(*.tif)
    file_list_2：浸水二値化画像(*.tif)
    file_list_3：浸水マップ(*.shp)
    
    関数：create_sarmap_folder
    引数1：2(固定)
    引数2：出力ディレクトリ名
    引数3：仙台SAR画像(*.tif)
    引数4：浸水二値化画像(*.tif)
    引数5：浸水マップ(*.shp)
    """
    parser = argparse.ArgumentParser(description="create_sarmap_folder")

    parser.add_argument("data_type_flg", choices=["flood", "landslide"])
    parser.add_argument("out_path")
    parser.add_argument("--data1", "-1", nargs="+")
    parser.add_argument("--data2", "-2", nargs="+")
    parser.add_argument("--data3", "-3", nargs="+")
    parser.add_argument("--data4", "-4", nargs="+")

    args = parser.parse_args()

    lists = []
    if args.data1 is not None:
        lists.append(args.data1)
    if args.data2 is not None:
        lists.append(args.data2)
    if args.data3 is not None:
        lists.append(args.data3)
    if args.data4 is not None:
        lists.append(args.data4)

    flg = 1 if args.data_type_flg == "landslide" else 2
    create_sarmap_folder(flg,
                         args.out_path,
                         *lists)


    
    exit(0)

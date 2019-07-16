# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: clip_value.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

from shapefile import Reader as ShpReader
from shapefile import Writer as ShpWriter

from os import path, makedirs
import argparse
from Common.constant import DATA_PATH_BASE


def clip_value(in_file, ot_dir, min_height, max_height):
    """
    オンライン学習４　ベクタデータのフィルタリング
    
    浸水・土砂崩れベクタデータをGISデータの属性値(値)を使用してフィルタリングするプログラムを実行します。
    
    関数  : clip_value
    引数1 : 浸水・土砂崩れベクタデータ(*.shp)
    引数2 : 出力ディレクトリ名
    引数3 : 出力対象となる値の最小値
    引数4 : 出力対象となる値の最大値
    
    """
    # Get actual file path
    in_file = path.join(DATA_PATH_BASE, in_file)
    ot_dir = path.join(DATA_PATH_BASE, ot_dir)
    makedirs(ot_dir, exist_ok=True)

    ot_file = path.join(ot_dir, "{0}v.tif".format(path.splitext(path.basename(in_file))[0]))

    reader = ShpReader(in_file, encoding='cp932')
    writer = ShpWriter(ot_file, encoding='cp932')

    # Create DBF schema
    height_col_id = None
    for i, col in enumerate((col for col in reader.fields if col[0] != "DeletionFlag")):
        if col[0] != "DeletionFlag":
            writer.field(col[0], col[1], col[2], col[3])
        if col[0] == "height":
            height_col_id = i

    if height_col_id is None:
        print("height column not found in polygon shapefile")
        return

    # Filtering
    n_mesh = reader.numRecords
    cnt_mesh = 0
    for data in reader.iterShapeRecords():
        height = data.record[height_col_id]
        if (height is not None) and (min_height <= height <= max_height):
            # This polygon is output target.
            writer.shape(data.shape)
            writer.record(*data.record)

        cnt_mesh = cnt_mesh + 1
        if cnt_mesh % 100000 == 0:
            print("{0}K / {1}K".format(cnt_mesh/1000, n_mesh/1000))

    writer.close()


if __name__ == "__main__":
    """
    オンライン学習４　ベクタデータのフィルタリング
    
    浸水・土砂崩れベクタデータをGISデータの属性値(値)を使用してフィルタリングするプログラムを実行します。
    
    関数  : clip_value
    引数1 : 浸水・土砂崩れベクタデータ(*.shp)
    引数2 : 出力ディレクトリ名
    引数3 : 出力対象となる値の最小値
    引数4 : 出力対象となる値の最大値
    
    """
    parser = argparse.ArgumentParser(description="clip_value")

    parser.add_argument("in_file")
    parser.add_argument("out_path")
    parser.add_argument("min_height", type=float)
    parser.add_argument("max_height", type=float)

    args = parser.parse_args()

    clip_value(args.in_file,
               args.out_path,
               args.min_height,
               args.max_height)
               
    exit(0)

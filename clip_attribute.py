# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: clip_attribute.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

from shapefile import Reader as ShpReader
from shapefile import Writer as ShpWriter
from shapely.geometry import Polygon

from os import path, makedirs
from Common.constant import DATA_PATH_BASE


def clip_attribute(in_mesh, in_mask, in_key, ot_dir, flg_mask):
    """
    オンライン学習４　ベクタデータのフィルタリング
    
    浸水・土砂崩れベクタデータをGISデータの属性値(文字列)を使用してフィルタリングします。
    
    関数  : clip_attribute
    引数1 : 浸水・土砂崩れベクタデータ(*.shp)
    引数2 : GISデータ(*.shp)
    引数3 : 属性キーファイル(*.key)
    引数4 : 出力ディレクトリ名
    引数5 : 出力フラグ(True：GISデータと重なる部分を出力、False：GISデータと重ならない部分を出力)
    
    """
    # Get actual file path
    in_mesh = path.join(DATA_PATH_BASE, in_mesh)
    in_mask = path.join(DATA_PATH_BASE, in_mask)
    in_key = path.join(DATA_PATH_BASE, in_key)
    ot_dir = path.join(DATA_PATH_BASE, ot_dir)
    makedirs(ot_dir, exist_ok=True)

    ot_file = path.join(ot_dir, "{0}a.tif".format(path.splitext(path.basename(in_mesh))[0]))

    reader_mesh = ShpReader(in_mesh, encoding='cp932')
    reader_mask = ShpReader(in_mask, encoding='cp932')
    writer = ShpWriter(ot_file, encoding='cp932')

    dic_name = {}
    for i, col in enumerate((col for col in reader_mask.fields if col[0] != "DeletionFlag")):
        dic_name[col[0]] = i

    # Read key file
    key_cond = {}
    for line in open(in_key, "r"):
        items = line.split(",")
        if items[0] not in dic_name:
            print("Attribute {0} not found in mask shapefile".format(items[0]))
            return
        key_cond[dic_name[items[0]]] = [v.strip() for v in items[1:]]

    # Create DBF schema
    for col in reader_mesh.fields:
        if col[0] != "DeletionFlag":
            writer.field(col[0], col[1], col[2], col[3])

    # Create set of mask polygon
    maskdata = []
    for data in reader_mask.iterShapeRecords():
        points = data.shape.points
        points_split = list(data.shape.parts) + [len(points)]
        record = data.record

        if check_record(record, key_cond):
            # Use as mask polygon only when all key conditions are satisfied.
            # Memorize shape and bbox of polygon.
            x_range = min(points, key=lambda x: x[0])[0], max(points, key=lambda x: x[0])[0]
            y_range = min(points, key=lambda x: x[1])[1], max(points, key=lambda x: x[1])[1]
            poly_list = []
            for i in range(len(points_split)-1):
                points_part = points[points_split[i]:points_split[i+1]]
                poly_list.append(Polygon(points_part))

            maskdata.append((x_range, y_range, poly_list))

    # Filtering
    n_mesh = reader_mesh.numRecords
    cnt_mesh = 0
    for data in reader_mesh.iterShapeRecords():
        center = Polygon(data.shape.points).centroid
        x = center.x
        y = center.y

        masked = False
        for x_range, y_range, mask_polys in maskdata:
            # Primary screening by mask polygon bbox.
            if x < x_range[0] or x > x_range[1] or y < y_range[0] or y > y_range[1]:
                continue

            mask_count = sum(poly.contains(center) for poly in mask_polys)
            if mask_count % 2 == 1:
                masked = True
                break

        if masked == flg_mask:
            # This polygon is output target.
            writer.shape(data.shape)
            writer.record(*data.record)

        cnt_mesh = cnt_mesh + 1
        if cnt_mesh % 100000 == 0:
            print("{0}K / {1}K".format(cnt_mesh/1000, n_mesh/1000))

    writer.close()


def check_record(record, key_cond):
    """
    Check if the record satisfies all key conditions
    :param record: record
    :param key_cond: key conditions
    :return: True if all satisfies, false otherwise.
    """
    for index in key_cond:
        keylist = key_cond[index]
        if record[index] not in keylist:
            # There is an attribute that does not satisfy the condition
            return False

    # All condition satisfied
    return True


if __name__ == "__main__":
    """
    オンライン学習４　ベクタデータのフィルタリング
    
    浸水・土砂崩れベクタデータをGISデータの属性値(文字列)を使用してフィルタリングします。
    
    関数  : clip_attribute
    引数1 : 浸水・土砂崩れベクタデータ(*.shp)
    引数2 : GISデータ(*.shp)
    引数3 : 属性キーファイル(*.key)
    引数4 : 出力ディレクトリ名
    引数5 : 出力フラグ(True：GISデータと重なる部分を出力、False：GISデータと重ならない部分を出力)
    
    """
    clip_attribute(r"",
                   r"",
                   r"",
                   r"",
                   )
                   
    exit(0)

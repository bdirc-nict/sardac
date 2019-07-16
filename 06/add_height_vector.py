# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: add_height_vector.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and Communications Technology
#==================================================================================

from shapefile import Reader as ShpReader
from shapefile import Writer as ShpWriter

from shapely.geometry import Point, Polygon

from grid_data import GridData


def add_height_vector(in_polys, in_hpoint, dst_fn):
    """
    オンライン学習3　被害領域の抽出、ラスタベクタ変換

    メッシュデータに標高値を付与します。
    
    関数   ： add_height_vector
    引数1  ： 入力メッシュデータ名(.tif)
    引数2  ： 数値標高ﾓﾃﾞﾙ名(.shp)
    引数3　： 出力ファイル名(.shp)

    """

    # Read DEM data
    print("loading DEM data ...")
    dem = GridData()
    dem_reader = ShpReader(in_hpoint, encoding='cp932')

    n_p = dem_reader.numRecords
    cnt_p = 0
    for data in dem_reader.iterShapeRecords():
        point = Point(data.shape.points[0])
        p_val = data.record

        dem.add_data(point.x, point.y, p_val)
        cnt_p = cnt_p + 1
        if cnt_p % 100000 == 0:
            print("{0}K / {1}K".format(cnt_p/1000, n_p/1000))
    print("loaded DEM data .")
    print()

    # Process each polygon shapefile
    for in_poly in in_polys:
        print("processing {0} ...".format(in_poly))
        poly_reader = ShpReader(in_poly)
        poly_writer = ShpWriter(target=dst_fn)

        # Create DBF schema
        for col in poly_reader.fields:
            if col[0] != "DeletionFlag":
                poly_writer.field(col[0], col[1], col[2], col[3])
        poly_writer.field("height", "N", 18, 9)

        # Attach elevation value
        n_poly = poly_reader.numRecords
        cnt_poly = 0
        for data in poly_reader.iterShapeRecords():
            center = Polygon(data.shape.points).centroid
            key_x = dem.search_nearest_x(center.coords[0][0])
            key_y = dem.search_nearest_y(center.coords[0][1])
            dem_record = dem.get_data(key_x, key_y)
            if dem_record:
                # Nearest grid point has elevation value
                record = data.record + dem_record
            else:
                # Nearest grid point doesn't have elevation value
                record = data.record + [None]

            poly_writer.shape(data.shape)
            poly_writer.record(*record)

            cnt_poly = cnt_poly + 1
            if cnt_poly % 100000 == 0:
                print("{0}K / {1}K".format(cnt_poly/1000, n_poly/1000))

        poly_writer.close()

        print("processed {0} .".format(in_poly))
        print()
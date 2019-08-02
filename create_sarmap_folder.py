# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: create_sarmap_folder_.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

from Common.input_txt_writer import InputTxtData
from Common.process_list_json import get_copy_files_from_json, get_meta_from_json
from db.db_connect import get_connection
from db.db_select import select_one_record
from db.db_execute import insert_with_commit

from os import path, makedirs, listdir
from shutil import copy2, rmtree
import time
import argparse

# ステージング用（すべて登録）
target_registers = ["raster", "vector", "rasvec"]

# 公開サーバー用
#target_registers = ["raster", "rasvec"]


def get_image_id(image_name, is_vector):
    with get_connection() as conn:
        row = select_one_record(conn, "select image_type_id from m_image_type where image_type_name = '{0}';".format(image_name))
        if row is not None:
            return row[0]
        new_order = select_one_record(conn, "select max(image_type_order) from m_image_type")[0] + 1
        if is_vector:
            new_id = select_one_record(conn, "select max(image_type_id) from m_image_type where image_type_id >= 1000;")[0] + 1
        else:
            new_id = select_one_record(conn, "select max(image_type_id) from m_image_type where image_type_id < 1000;")[0] + 1
        insert_with_commit(conn, "m_image_type", {
            "image_type_id": new_id,
            "image_type_name": image_name,
            "image_type_order": new_order,
            "delete_flag": False,
            "registration_date": ("raw", "now()"),
            "updated_date": ("raw", "now()")
        })
        return new_id


def create_input_datas(target_files, meta):
    time_str = time.strftime("%Y%m%d%H%M%S")
    input_datas = {}

    data_type_id = int(meta["data_type_id"])
    area_id = int(meta["area_id"])
    title = meta["title"]
    mode = meta["mode"]
    survey_area = meta["survey_area"]
    aircraft_height = meta["aircraft_height"]
    aircraft_direction = meta["aircraft_direction"]
    term_from = meta["term_from"]
    term_to = meta["term_to"]

    for image_type in target_files:
        is_vector = len([src for src in target_files[image_type] if path.splitext(src)[1] == ".shp"]) > 0
        image_id = get_image_id(image_type, is_vector)

        data = InputTxtData()
        data.time_str = time_str
        data.data_type_id = data_type_id
        data.image_type_id = image_id
        data.image_type = image_type
        data.area_type_id = area_id
        data.title = title
        data.mode = mode
        data.survey_area = survey_area
        data.aircraft_height = aircraft_height
        data.aircraft_direction = aircraft_direction
        data.term_from = term_from
        data.term_to = term_to
        data.image_date = ""

        input_datas[image_type] = data

    return input_datas


def create_sarmap_folder(in_file, ot_dir):
    publish_dir = path.join(ot_dir, "geoserver")

    target_files = get_copy_files_from_json(in_file, target_registers)
    meta = get_meta_from_json(in_file)

    if path.exists(publish_dir) and len(listdir(publish_dir)) > 0:
        message = "\n".join(["Geoserver公開用データの出力先\"{0}\"が空ではありません。".format(publish_dir),
                             "空でない場所に出力した場合、既存のファイルが登録に影響を与える場合があります。",
                             "続行しますか？",
                             "y:そのまま続行",
                             "Y:既存ファイルを削除して続行",
                             "n:中止"])
        print(message)

        while True:
            get = input("[y/Y/n]")
            if get == "n":
                return
            if get == "y":
                break
            if get == "Y":
                rmtree(publish_dir)
                break
        makedirs(publish_dir)

    input_datas = create_input_datas(target_files, meta)
    for image_type in target_files:
        image_id = input_datas[image_type].image_type_id
        target_path = path.join(publish_dir, str(image_id))
        makedirs(target_path)

        for file in target_files[image_type]:
            copy2(file, target_path)
            # shapefileの場合にはshxやdbfも正しく記載する想定とする
            #if path.splitext(file)[1] == ".shp":
            #    dbf_path = path.splitext(file)[0] + ".dbf"
            #    shx_path = path.splitext(file)[0] + ".shx"
            #    copy2(dbf_path, target_path)
            #    copy2(shx_path, target_path)

        input_datas[image_type].write_file(target_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="create_sarmap_folder")

    parser.add_argument("in_file")
    parser.add_argument("out_path")

    args = parser.parse_args()

    create_sarmap_folder(args.in_file,
                         args.out_path)

    exit(0)

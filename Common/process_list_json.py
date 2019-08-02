from os import path
import json


def get_copy_files_from_json(json_path, registers):
    base_dir = path.dirname(json_path)

    f = open(json_path, "r")
    data = json.load(f)
    f.close()

    outlist = sum((item["output"] for item in data["list"]), [])

    image_type_list = list(set(item["image_type"] for item in outlist if "register" in item and item["register"] in registers))

    filelists = {im_type: [] for im_type in image_type_list}
    for out_item in outlist:
        if "register" in out_item and out_item["register"] in registers:
            filelists[out_item["image_type"]].append(path.join(base_dir, out_item["name"]))

    return filelists


def get_meta_from_json(json_path):
    target_keys = ["data_type_id", "area_id", "title", "mode", "survey_area", "aircraft_height",
                   "aircraft_direction", "term_from", "term_to"]

    f = open(json_path, "r")
    data = json.load(f)
    f.close()

    return {k: data[k] for k in target_keys}

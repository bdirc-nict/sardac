# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: gdal_command.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

from os import path
import re
from subprocess import Popen, PIPE

GDAL_BASE = r"/usr/local/bin/"
BIN_EXT = ""


def gdalinfo(filename):
    """
    Execute "gdalinfo" command.
    :param filename: path of image file.
    :return: dictionary for image information.
    """
    bin_path = path.join(GDAL_BASE, "gdalinfo"+BIN_EXT)

    p = Popen([bin_path, filename], stdout=PIPE)
    out, err = p.communicate()

    result = {"cornerCoordinates": {}}
    for line in out.decode('utf-8').split('\n'):
        re_result = re.match(r" *Pixel Size *= *\( *([-+0-9\.]+) *, *([-+0-9\.]+) *\)", line)
        if re_result:
            result["pixel_size"] = (float(re_result.group(1)), float(re_result.group(2)))
            continue
        re_result = re.match(r" *Upper Left * *\( *([-+0-9\.]+) *, *([-+0-9\.]+) *\)", line)
        if re_result:
            result["cornerCoordinates"]["upperLeft"] = (float(re_result.group(1)), float(re_result.group(2)))
            continue
        re_result = re.match(r" *Lower Right *\( *([-+0-9\.]+) *, *([-+0-9\.]+) *\)", line)
        if re_result:
            result["cornerCoordinates"]["lowerRight"] = (float(re_result.group(1)), float(re_result.group(2)))
            continue
        re_result = re.match(r" *Center * *\( *([-+0-9\.]+) *, *([-+0-9\.]+) *\)", line)
        if re_result:
            result["cornerCoordinates"]["center"] = (float(re_result.group(1)), float(re_result.group(2)))
            continue

    return result


def gdaltranslate_resolution(dest, src, x_resolution, y_resolution, resample="average", out_area=None):
    """
    Execute "gdal_translate" with specified resolution.
    :param dest: The destination file name
    :param src: The source file name
    :param x_resolution: resolution of X
    :param y_resolution: resolution of Y
    :param resample: resampling algorithm
    :param out_area: Specify area to output as an image in [west longitude, east longitude, north latitude, south latitude] format. If not specified, the same area as the source image is output.
    :return: return code for "gdal_translate" command.
    """
    bin_path = path.join(GDAL_BASE, "gdal_translate"+BIN_EXT)

    param = ["-tr", str(x_resolution), str(y_resolution), "-r", resample]
    if out_area:
        param = param + ["-projwin", str(out_area[0]), str(out_area[1]), str(out_area[2]), str(out_area[3])]
    param = param + [src, dest]
    p = Popen([bin_path] + param)
    p.wait()
    print(p.returncode)


def gdaltranslate_gcp(dest, src, gcp, out_srs="EPSG:4326", x_resolution=None, y_resolution=None):
    """
    Execute "gdal_translate" command with the correspondence between image coordinates and world coordinates
    :param dest: The destination file name
    :param src: The source file name
    :param gcp: the indicated ground control point to the output. specify in list of [X coordinates, Y coordinates, longitude, latitude].
    :param out_srs: EPSG for destination file
    :param x_resolution: X resolution
    :param y_resolution: Y resolution
    :return: return code for "gdal_translate" command.
    """
    bin_path = path.join(GDAL_BASE, "gdal_translate"+BIN_EXT)

    param = ["-projwin_srs", out_srs, "-of", "GTiff"]
    for gcp_record in gcp:
        param.append("-gcp")
        for v in gcp_record:
            param.append(str(v))
    if x_resolution and y_resolution:
        param = param + ["-tr", str(x_resolution), str(y_resolution)]
    param = param + [src, dest]
    p = Popen([bin_path] + param)
    p.wait()
    print(p.returncode)


def gdaltranslate_a_ullr(dest, src, lon1,lon2,lat1,lat2, out_srs="EPSG:4326"):
    """
    Execute "gdal_translate" command with the upper-left and lower-right coordinates.
    :param dest: The destination file name
    :param src: The source file name
    :param lon1: west longitude
    :param lon2: east longitude
    :param lat1: north latitude
    :param lat2: south latitude
    :param out_srs: EPSG for destination file
    :return: return code for "gdal_translate" command.
    """
    bin_path = path.join(GDAL_BASE, "gdal_translate"+BIN_EXT)

    param = ["-projwin_srs", out_srs, "-of", "GTiff", "-a_ullr", str(lon1), str(lat1), str(lon2), str(lat2)]
    param = param + [src, dest]
    p = Popen([bin_path] + param)
    p.wait()
    print(p.returncode)


def gdalwarp(dest, src, src_srs="EPSG:4326", resample="cubic", dest_nodata=0, x_resolution=None, y_resolution=None):
    """
    Execute "gdalwarp" command.
    :param dest: The destination file name
    :param src: The source file name
    :param src_srs: EPSG for source file
    :param resample: resampling algorithm
    :param dest_nodata: Value representing nodata of destination file
    :param x_resolution: X resolution
    :param y_resolution: Y resolution
    :return: return code for "gdalwarp" command.
    """
    bin_path = path.join(GDAL_BASE, "gdalwarp"+BIN_EXT)

    param = ["-s_srs", src_srs, "-r", resample, "-dstnodata", str(dest_nodata), "-of", "GTiff"]
    if x_resolution and y_resolution:
        param = param + ["-tr", str(x_resolution), str(y_resolution)]
    param = param + [src, dest]
    p = Popen([bin_path] + param)
    p.wait()
    print(p.returncode)

# coding: utf-8

# Copyright (c) 2019 National Institute of Information and Communications Technology
# Released under the GPLv2 license

import numpy as np
import cv2
from tifffile import imsave
from .gdal_command import gdalinfo, gdaltranslate_resolution, gdaltranslate_a_ullr
from .constant import DEV_FLAG
from math import sin, cos, sqrt, radians
from os import path, remove

class RectGeoTiffCoordinateCalculator:
    """
    Class to manage Geotiff coordinate information.
    """
    def __init__(self, tiffpath):
        self.tiffpath = tiffpath
        self.info = gdalinfo(tiffpath)
        self.lon_range = [self.info["cornerCoordinates"]["upperLeft"][0], self.info["cornerCoordinates"]["lowerRight"][0]]
        self.lat_range = [self.info["cornerCoordinates"]["upperLeft"][1], self.info["cornerCoordinates"]["lowerRight"][1]]
        self.pixel_lon = self.info["pixel_size"][0]
        self.pixel_lat = self.info["pixel_size"][1]

    def get_center(self):
        """
        :return: center coordinate (longitude, latitude)
        """
        coord = self.info["cornerCoordinates"]["center"]
        return coord[0], coord[1]

    def get_upper_left(self):
        """
        Get upper-left coordinates of the image.
        :return: upper-left coordinate (longitude, latitude)
        """
        return self.lon_range[0], self.lat_range[0]

    def get_lower_right(self):
        """
        Get lower-right coordinates of the image.
        :return: lower-right coordinate (longitude, latitude)
        """
        return self.lon_range[1], self.lat_range[1]

    def get_lon_on_pixel_index(self, x_index):
        """
        Get Longitude of the specified X position.
        :param x_index: X position of the image
        :return: longitude of specify position
        """
        return self.lon_range[0] + x_index * self.pixel_lon

    def get_lat_on_pixel_index(self, y_index):
        """
        Get Latitude of the specified Y position.
        :param y_index: Y position of the image
        :return: latitude of specify position
        """
        return self.lat_range[0] + y_index * self.pixel_lat


def create_res5m_tiff(src_fn, dst_fn, out_area=None):
    """
    Convert geotiff image to 5m resolution.
    :param src_fn: The source Geotiff file
    :param dst_fn: The destination Geotiff file
    :param out_area: Specify area to output as an image in [west longitude, east longitude, north latitude, south latitude] format. If not specified, the same area as the source image is output.
    """
    # Read the input image and determine the size of the pixel
    lon_5m, lat_5m = get_5m_degree(src_fn)

    # Create an image of specified resolution
    # http://www7b.biglobe.ne.jp/~oyama/GDAL/gdal.html
    gdaltranslate_resolution(dst_fn, src_fn, lon_5m, lat_5m, out_area=out_area)


def get_5m_degree(src_fn):
    """
    Get how many degree will be 5m in longitude and latitude at center of image.
    :param src_fn: The source Geotiff file
    :return: longitude and latitude degree of 5m
    """
    # Get center latitude of source image.
    center_lat = RectGeoTiffCoordinateCalculator(src_fn).get_center()[1]

    # Calculate distance for 1 degree of longitude and latitude [m/deg]

    # Longitude direction
    # 6378137m = Earth's equatorial radius
    # 1/298.257222101 =  Earth's Flat rate
    lat_rad = radians(center_lat)
    f = 1 / 298.257222101
    e2sin2 = f*(2-f) * sin(lat_rad)*sin(lat_rad)
    meter_onedeg_x = radians(1) * 6378137 * cos(lat_rad) / sqrt(1-e2sin2)

    # Latitude direction
    # 4007862m = Latitude 360 degrees distance
    meter_onedeg_y = 40007862 / 360

    # [m] / [m/deg] = [deg]
    return 5 / meter_onedeg_x, 5 / meter_onedeg_y


def get_threshold(data, nodata=None):
    """
    Calculate the threshold from the image by Discriminant analysis.
    :param data: Numpy array of source Geotiff.
    :param nodata: Value representing nodata of source Geotiff
    :return: Threshold
    """
    tmp = data.flatten()
    # If a value of NODATA is specified, exclude the data of that value
    if nodata:
        tmp = tmp[~(tmp==nodata)]

    threshold = cv2.threshold(tmp, 0, 255, cv2.THRESH_OTSU)[0]

    return threshold


def create_binary_array(src_matrix, threshold, small_value, large_value, src_nodata=0, dst_nodata=0):
    """
    Create binarized image.
    :param src_matrix: Numpy array of source Geotiff.
    :param threshold: Threshold
    :param small_value: Value to be set to pixel below threshold
    :param large_value: Value to be set to pixel above threshold
    :param src_nodata: Value representing nodata of source Geotiff
    :param dst_nodata: Value representing nodata of destination Geotiff
    :return: Numpy array of binarized image
    """
    bin = np.zeros(shape=src_matrix.shape, dtype=np.uint8)
    bin[(src_matrix < threshold) & (src_matrix != src_nodata)] = small_value
    bin[(src_matrix >= threshold) & (src_matrix != src_nodata)] = large_value
    bin[(src_matrix == src_nodata)] = dst_nodata
    return bin


def trans_geotiff(dst_fn, src_matrix, base_geotiff):
    """
    Save the numpy array as geotiff. Use existing geotiff coordinate information.
    :param dst_fn: The destination path
    :param src_matrix: Numpy array of an image
    :param base_geotiff: Geotiff file used coordinate information
    """
    # Get Geotiff image coordinates
    info = RectGeoTiffCoordinateCalculator(base_geotiff)
    ul_x, ul_y = info.get_upper_left()
    br_x, br_y = info.get_lower_right()

    # Create destination image

    tmp_path1 = path.join(path.dirname(dst_fn), "tmp_save1.tif")
    imsave(tmp_path1, src_matrix)
    gdaltranslate_a_ullr(dst_fn, tmp_path1, ul_x,br_x,ul_y,br_y)
    if not DEV_FLAG:
        remove(tmp_path1)


def average_filter(img, filtersize_az, filtersize_gr):
    """
    Create averaged image.
    :param img: Numpy array of an image
    :param filtersize_az: filter size of AZ direction
    :param filtersize_gr: filter size of GR direction
    :return: Numpy array of filtered image
    """
    return cv2.blur(img, (filtersize_az, filtersize_gr))

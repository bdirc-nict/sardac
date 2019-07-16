# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: grid_data.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and Communications Technology
#==================================================================================

from bisect import bisect_left


class GridData:
    """
    Class to manage grid data.
    """

    def __init__(self):
        self.all_data = {}
        self.x_list = []
        self.y_list = []

    def add_data(self, x, y, record):
        """
        Add new data.
        :param x: X Coordinate
        :param y: Y Coordinate
        :param record: value
        """
        self.all_data[(x, y)] = record
        self.add_value_to_x_list(x)
        self.add_value_to_y_list(y)

    def get_data(self, x, y):
        """
        Get the data of Specified position
        :param x: X Coordinate
        :param y: Y Coordinate
        :return: data of Specified position, None if no data exists
        """
        if (x, y) in self.all_data:
            return self.all_data[(x, y)]
        return None

    def add_value_to_x_list(self, value):
        """
        Add X coordinate to X coordinate list
        :param value: X coordinate
        """
        if len(self.x_list) == 0:
            self.x_list.append(value)
        else:
            pos = bisect_left(self.x_list, value)
            if pos == len(self.x_list) or self.x_list[pos] != value:
                self.x_list.insert(pos, value)

    def add_value_to_y_list(self, value):
        """
        Add Y coordinate to Y coordinate list
        :param value: Y coordinate
        """
        if len(self.y_list) == 0:
            self.y_list.append(value)
        else:
            pos = bisect_left(self.y_list, value)
            if pos == len(self.y_list) or self.y_list[pos] != value:
                self.y_list.insert(pos, value)

    def search_nearest_x(self, x):
        """
        Get value nearest to given X coordinate from X coordinate list
        :param x: X coordinate
        :return: nearest X coordinate
        """
        pos = bisect_left(self.x_list, x)
        if pos == 0:
            return self.x_list[0]
        if pos == len(self.x_list):
            return self.x_list[-1]

        v0 = self.x_list[pos - 1]
        v1 = self.x_list[pos]

        if v1 - x < x - v0:
            return v1
        else:
            return v0

    def search_nearest_y(self, y):
        """
        Get value nearest to given Y coordinate from Y coordinate list
        :param y: Y coordinate
        :return: nearest Y coordinate
        """
        pos = bisect_left(self.y_list, y)
        if pos == 0:
            return self.y_list[0]
        if pos == len(self.y_list):
            return self.y_list[-1]

        v0 = self.y_list[pos - 1]
        v1 = self.y_list[pos]

        if v1 - y < y - v0:
            return v1
        else:
            return v0

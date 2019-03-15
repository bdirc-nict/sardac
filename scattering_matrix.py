# coding: utf-8

# Copyright (c) 2019 National Institute of Information and Communications Technology
# Released under the GPLv2 license

from ctypes import *
import numpy as np
import numpy.ctypeslib as ctypeslib
from math import ceil
from os import path

# load shared library
script_dir = path.dirname(path.abspath(__file__))
dll_dir = path.abspath(path.join(script_dir, "Common", "Lib", "CreateScatteringMatrix.so"))
_lib = ctypeslib.load_library(dll_dir, ".")


def create_scattering_matrix(in_file, n_az, n_gr, win_az, win_gr):
    """
    Execute binary file reading process defined in shared library
    :param in_file: The source file name
    :param n_az: AZ direction width of source data
    :param n_gr: GR direction width of source data
    :param win_az: multi-look size of AZ direction
    :param win_gr: multi-look size of GR direction
    :return: Complex matrix after multi-look processing
    """

    # Image size after multi-look processing
    n_img_az = ceil(n_az / win_az)
    n_img_gr = ceil(n_gr / win_gr)
    n_img = (n_img_az, n_img_gr)

    # create parameter for reading process
    matrix_type = ctypeslib.ndpointer(dtype=c_float, ndim=2, shape=n_img, flags='C')
    _lib._Z22CreateScatteringMatrixPcPfS0_iiii.argtypes = [c_char_p, matrix_type, matrix_type, c_int32,c_int32,c_int32,c_int32]
    _lib._Z22CreateScatteringMatrixPcPfS0_iiii.restype = c_int32

    matrix_re = np.zeros(shape=n_img, dtype=np.float32)
    matrix_im = np.zeros(shape=n_img, dtype=np.float32)

    _in_file = c_char_p(in_file.encode())
    _n_az = c_int(n_az)
    _n_gr = c_int(n_gr)
    _win_az = c_int(win_az)
    _win_gr = c_int(win_gr)

    # Execute reading process
    _lib._Z22CreateScatteringMatrixPcPfS0_iiii(_in_file, matrix_re, matrix_im, _n_az, _n_gr, _win_az, _win_gr)
    print()

    matrix = matrix_re + 1j * matrix_im
    matrix.astype(np.complex64)

    return matrix


if __name__ == '__main__':
    infile = r"D:\projectdata\NICT\data\Sendai01.mgp_HHm"
    ncols = 24000
    nrows = 24000
    xwin = 10
    ywin = 10

    m1, m2 = create_scattering_matrix(infile, ncols, nrows, xwin, ywin)

    print(m1)
    print(m2)

    print(np.min(m1))
    print(np.min(m2))
    print(np.max(m1))
    print(np.max(m2))

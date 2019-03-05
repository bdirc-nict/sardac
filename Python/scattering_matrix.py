from ctypes import *
import numpy as np
import numpy.ctypeslib as ctypeslib
from math import ceil
from os import path

# DLL設定
script_dir = path.dirname(path.abspath(__file__))
dll_dir = path.abspath(path.join(script_dir, "Common", "Dll", "CreateScatteringMatrix.dll"))
_lib = ctypeslib.load_library(dll_dir, ".")


def create_scattering_matrix(in_file, n_az, n_gr, win_az, win_gr):
    """
    マルチルック処理付きのバイナリファイル読み込み処理を実行する
    :param in_file: バイナリファイルのパス
    :param n_az: 元データのAz方向幅
    :param n_gr: 元データのGr方向幅
    :param win_az: マルチルック数（Az方向）
    :param win_gr: マルチルック数（Gr方向）
    :return: マルチルック処理後のデータ（複素数）
    """

    # マルチルック処理後の画像サイズ
    n_img_az = ceil(n_az / win_az)
    n_img_gr = ceil(n_gr / win_gr)
    n_img = (n_img_az, n_img_gr)

    # DLLへ渡すパラメータの作成
    matrix_type = ctypeslib.ndpointer(dtype=c_float, ndim=2, shape=n_img, flags='C')
    _lib.CreateScatteringMatrix.argtypes = [c_char_p, matrix_type, matrix_type, c_int32,c_int32,c_int32,c_int32]
    _lib.CreateScatteringMatrix.restype = c_int32

    matrix_re = np.zeros(shape=n_img, dtype=np.float32)
    matrix_im = np.zeros(shape=n_img, dtype=np.float32)

    _in_file = c_char_p(in_file.encode())
    _n_az = c_int(n_az)
    _n_gr = c_int(n_gr)
    _win_az = c_int(win_az)
    _win_gr = c_int(win_gr)

    # DLL内の処理を実行
    _lib.CreateScatteringMatrix(_in_file, matrix_re, matrix_im, _n_az, _n_gr, _win_az, _win_gr)
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


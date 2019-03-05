import numpy as np
from Common.mgp_info_reader import read_mgp_info, get_data, get_decimal_from_sexagesimal
from scattering_matrix import create_scattering_matrix
from covariance_matrix import create_covariance_matrix

from tifffile import imsave
import gdal,gdalconst

from math import ceil, log10
from os import path, makedirs, remove
import time


# 結果をfloatで出す場合はTrue、uint8で出す場合はFalse
image_float = False

format_name = "GTiff"


def create_comp_image(in_hh, in_hv, in_vv, in_info, ot_dir_base, win_az, win_gr):
    """
    衛星画像の生データから、画像を作成する。
    :param in_hh: SARデータ（HH成分)
    :param in_hv: SARデータ（HV成分）
    :param in_vv: SARデータ（VV成分）
    :param in_info: SAR観測諸元ﾌｧｲﾙ
    :param ot_dir_base: 出力ディレクトリ名
    :param win_az: 平均化ｳｨﾝﾄﾞｳ(X方向)
    :param win_gr: 平均化ｳｨﾝﾄﾞｳ(Y方向)
    """
    # 実際のファイル出力先
    ot_dir = path.join(ot_dir_base, "1")
    makedirs(ot_dir, exist_ok=True)

    # ファイル名設定
    basename = path.splitext(path.basename(in_hh))[0]
    fn_single = path.join(ot_dir, "tmp_{0}_base.tif".format(basename))
    fn_single_trans = path.join(ot_dir, "tmp_{0}_trans.tif".format(basename))

    read_mgp_info(in_info)

    # 元の値から画素値を計算するためのパラメータ
    #2019.3.1 KY
    #mR = -5
    #mG = -10.5
    #mB = -6.5
    #sR = 7.5
    #sG = 7.5
    #sB = 7.5
    #2019.3.1 KY

    n_az = int(get_data("IMAGE_SIZE_AZ"))
    n_gr = int(get_data("IMAGE_SIZE_GR"))
    n_img_az = ceil(n_az / win_az)
    n_img_gr = ceil(n_gr / win_gr)

    # バイナリファイルを読み込む
    print("band 1 read ...")
    hh = create_scattering_matrix(in_hh, n_az, n_gr, win_az, win_gr)
    print("band 2 read ...")
    hv = create_scattering_matrix(in_hv, n_az, n_gr, win_az, win_gr)
    print("band 3 read ...")
    vv = create_scattering_matrix(in_vv, n_az, n_gr, win_az, win_gr)
    
    #2019.3.4 KY
    #c_11,c_12,c_13,c_22,c_23,c_33 = create_covariance_matrix(hh,hv,vv,1,1)
    #imsave(r"D:\NICT\2018\data\c11.tif",np.array(c_11.real()))
    #imsave(r"D:\NICT\2018\data\c22.tif",np.array(c_22.real()))
    #imsave(r"D:\NICT\2018\data\c33.tif",np.array(c_33.real()))
    
    #2019.3.4 KY
    
    # 対数変換、ヒストグラム調整
    #2019.3.1 KY
    #matrix_r = exband_histgram(logarithm_trans(hh), mR, sR)
    #matrix_g = exband_histgram(logarithm_trans(hv), mG, sG)
    #matrix_b = exband_histgram(logarithm_trans(vv), mB, sB)
    matrix_r = exband_histgram(logarithm_trans(hh))
    matrix_g = exband_histgram(logarithm_trans(hv))
    matrix_b = exband_histgram(logarithm_trans(vv))
    #2019.3.1 KY
    
    # tiff画像の作成
    imsave(r"D:\NICT\2018\data\hh.tif",matrix_r)
    imsave(r"D:\NICT\2018\data\hv.tif",matrix_g)
    imsave(r"D:\NICT\2018\data\vv.tif",matrix_b)
    
    imsave(fn_single, np.stack([matrix_r, matrix_g, matrix_b]))

    # translateで画像のGeotiff化を行う
    print("GDAL Translate ...")
    lonlat_ln = (get_decimal_from_sexagesimal(get_data("LATE_NEAR_LONG")), get_decimal_from_sexagesimal(get_data("LATE_NEAR_LAT")))
    lonlat_lf = (get_decimal_from_sexagesimal(get_data("LATE_FAR_LONG")), get_decimal_from_sexagesimal(get_data("LATE_FAR_LAT")))
    lonlat_en = (get_decimal_from_sexagesimal(get_data("EARLY_NEAR_LONG")), get_decimal_from_sexagesimal(get_data("EARLY_NEAR_LAT")))
    lonlat_ef = (get_decimal_from_sexagesimal(get_data("EARLY_FAR_LONG")), get_decimal_from_sexagesimal(get_data("EARLY_FAR_LAT")))
    gcp1 = gdal.GCP(lonlat_ln[0], lonlat_ln[1], 0, 0, 0)
    gcp2 = gdal.GCP(lonlat_lf[0], lonlat_lf[1], 0, 0, n_img_gr-1)
    gcp3 = gdal.GCP(lonlat_en[0], lonlat_en[1], 0, n_img_az-1, 0)
    gcp4 = gdal.GCP(lonlat_ef[0], lonlat_ef[1], 0, n_img_az-1, n_img_gr-1)
    translate_option = gdal.TranslateOptions(format=format_name, outputSRS="EPSG:4326", GCPs=[gcp1, gcp2, gcp3, gcp4])
    gdal.Translate(fn_single_trans, fn_single, options=translate_option)

    # gdal warp
    print("GDAL Warp ...")
    fn_single_warp = path.join(ot_dir, "{0}_{1}c.tif".format(basename, time.strftime("%Y%m%d%H%M%S")))
    nodata_value = -99 if image_float else 0
    warp_option = gdal.WarpOptions(srcSRS="EPSG:4326", resampleAlg=gdalconst.GRA_Cubic,  dstNodata=nodata_value)
    gdal.Warp(fn_single_warp, fn_single_trans, options=warp_option)

    # 一時ファイルの削除
    remove(fn_single)
    remove(fn_single_trans)


# 2019.3.1 KY
#def exband_histgram(src_matrix, m, s):
def exband_histgram(src_matrix):
# 2019.3.1 KY
    """
    ヒストグラム調整を行う
    μ-0.5σが20、μ+0.5σが150になるように線形変換する（μ、σはパラメータ）
    :param src_matrix: マルチルック後のデータ
    :param m: 変換パラメータ（平均）
    :param s: 変換パラメータ（標準偏差）
    :return: 変換後のデータ
    """
    # inf、nanを0に置き換える
    src_matrix = np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)
    
    #2019.3.1 KY
    #src_avg = 0 #np.mean(src_mat)
    #src_std = 0 #np.std(src_mat)
    #tmp_avg = src_avg + m
    #tmp_std = src_std + s

    # μ-0.5σが0、μ+0.5σが1になる線形変換、範囲外を0～1に収める
    #src_matrix = (src_matrix - tmp_avg) / (2 * tmp_std) + 0.5
    #src_matrix[src_matrix < 0] = 0
    #src_matrix[src_matrix > 1] = 1
    #2019.3.1 KY
    
    # 最小値が20、最大値が150になる線形変換
    #2019.3.1 KY
    #min_value = 0
    #max_value = 1
    min_value = src_matrix.min()
    max_value = src_matrix.max()
    #min_result = 20
    #max_result = 200
    min_result = 20
    max_result = 235
    #2019.3.1 KY
    

    # 変換前→変換後の傾きと、変換前が0の場合の値
    grad = (max_result - min_result) / (max_value - min_value)
    intercept = min_result - min_value * grad
    src_matrix = src_matrix * grad + intercept
    
    #2019.3.1 KY
    src_matrix = (src_matrix - src_matrix.mean()) / src_matrix.std() * 50 + src_matrix.mean()
    #2019.3.1 KY

    # 結果が20～150の範囲外、infやnanになることはないと思うけど念のため
    src_matrix[src_matrix < min_result] = min_result
    src_matrix[src_matrix > max_result] = max_result
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    if image_float:
        return src_matrix.astype(np.float32)
    else:
        return src_matrix.astype(np.uint8)


def logarithm_trans(src_matrix):
    """
    複素数行列を、絶対値計算・対数変換した値を返す
    :return: 対数変換を行った結果
    """
    return np.vectorize(lambda x: (log10(x) * 10 if x != 0 else -np.inf))(np.abs(src_matrix))



if __name__ == "__main__":
   create_comp_image(r"D:\NICT\2018\data\Obs09_aso-bridge\Obs09_aso-bridge.mgp_HHm",
                    r"D:\NICT\2018\data\Obs09_aso-bridge\Obs09_aso-bridge.mgp_HVm",
                    r"D:\NICT\2018\data\Obs09_aso-bridge\Obs09_aso-bridge.mgp_VVm",
                    r"D:\NICT\2018\data\Obs09_aso-bridge\Obs09_aso-bridge.mgp_HHm_info",
                    r"D:\NICT\2018\data",
                      10, 10)

    #create_comp_image(r"D:\NICT\2018\data\Sendai01\Sendai01.mgp_HHm",
    #                r"D:\NICT\2018\data\Sendai01\Sendai01.mgp_HVm",
    #                r"D:\NICT\2018\data\Sendai01\Sendai01.mgp_VVm",
    #                r"D:\NICT\2018\data\Sendai01\Sendai01.mgp_HHm_info",
    #                r"D:\NICT\2018\data",
    #                  10, 10)

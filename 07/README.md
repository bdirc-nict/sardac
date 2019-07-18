
マップ      ：なる早！どこどこマップ
対象        ：熊本地震（阿蘇大橋付近データ）
入力データ  ：
    災害前SARバイナリ（HH偏波）データ   ：Obs15_aso-bridge.mgp_HHm
    災害前SARバイナリ（HV偏波）データ   ：Obs15_aso-bridge.mgp_HVm
    災害前SARバイナリ（VV偏波）データ   ：Obs15_aso-bridge.mgp_VVm
    災害前諸元データ                    ：Obs15_aso-bridge.mgp_HHm_info
    災害後SARバイナリ（HH偏波）データ   ：Obs09_aso-bridge.mgp_HHm
    災害後SARバイナリ（HV偏波）データ   ：Obs09_aso-bridge.mgp_HVm
    災害後SARバイナリ（VV偏波）データ   ：Obs09_aso-bridge.mgp_VVm
    災害後諸元データ                    ：Obs09_aso-bridge.mgp_HHm_info
    

1.災害前後差分画像の作成

コマンド：python3.6 diffData/create_diiff_image.py in_file1_hh in_file1_hv in_file1_vv in_file1_info in_file2_hh in_file2_hv in_file2_vv in_file2_info out_path filter_size_az filter_size_gr


in_file1_hh	    ：災害前SARバイナリ(HH偏波)データ（*.mgp_HHm）
in_file1_hv	    ：災害前SARバイナリ(HV偏波)データ（*.mgp_HVm）
in_file1_vv	    ：災害前SARバイナリ(VV偏波)データ（*.mgp_VVm）
in_file1_info	：災害前諸元データ（*.mgp_HHm）
in_file2_hh	    ：災害後SARバイナリ(HH偏波)データ（*.mgp_HHm）
in_file2_hv	    ：災害後SARバイナリ(HV偏波)データ（*.mgp_HVm）
in_file2_vv	    ：災害後SARバイナリ(VV偏波)データ（*.mgp_VVm）
in_file2_info	：災害後諸元データ（*.mgp_HHm）
out_path	    ：出力ディレクトリ
filter_size_az	：マルチルックサイズ（アジマス方向）
filter_size_gr	：マルチルックサイズ（グランドレンジ方向）


2.G4U画像の生成

コマンド：python3.6 G4U/create_comp_image.py in_file_hh in_file_hv in_file_vv in_file_info out_path filter_size_az filter_size_gr

in_file_hh	    ：災害後SARバイナリ(HH偏波)データ（*.mgp_HHm）
in_file_hv	    ：災害後SARバイナリ(HV偏波)データ（*.mgp_HVm）
in_file_vv	    ：災害後SARバイナリ(VV偏波)データ（*.mgp_VVm）
in_file_info	：災害後諸元データ（*.mgp_HHm）
out_path	    ：出力ディレクトリ
filter_size_az	：マルチルックサイズ（アジマス方向）
filter_size_gr	：マルチルックサイズ（グランドレンジ方向）


3.Hα画像の生成

コマンド：python3.6 Halpha/create_comp_image.py in_file_hh in_file_hv in_file_vv in_file_info out_path filter_size_az filter_size_gr

in_file_hh	    ：災害後SARバイナリ(HH偏波)データ（*.mgp_HHm）
in_file_hv	    ：災害後SARバイナリ(HV偏波)データ（*.mgp_HVm）
in_file_vv	    ：災害後SARバイナリ(VV偏波)データ（*.mgp_VVm）
in_file_info	：災害後諸元データ（*.mgp_HHm）
out_path	    ：出力ディレクトリ
filter_size_az	：マルチルックサイズ（アジマス方向）
filter_size_gr	：マルチルックサイズ（グランドレンジ方向）



マップ      ：速報避難所危険度評価マップ
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
    

1.単偏波合成画像（災害前）の生成

コマンド：python3.6 create_comp_image.py in_file_hh in_file_hv in_file_vv in_file_info out_path filter_size_az filter_size_gr

in_file_hh	        ：災害前SARバイナリ(HH偏波)データ（*.mgp_HHm）
in_file_hv	        ：災害前SARバイナリ(HV偏波)データ（*.mgp_HVm）
in_file_vv	        ：災害前SARバイナリ(VV偏波)データ（*.mgp_VVm）
in_file_info	    ：災害前諸元データ（*.mgp_HHm）
out_path	        ：出力ディレクトリ
filter_size_az	    ：マルチルックサイズ（アジマス方向）
filter_size_gr	    ：マルチルックサイズ（グランドレンジ方向）


2.単偏波合成画像（災害後）の生成

コマンド：python3.6 create_comp_image.py in_file_hh in_file_hv in_file_vv in_file_info out_path filter_size_az filter_size_gr

in_file_hh	        ：災害後SARバイナリ(HH偏波)データ（*.mgp_HHm）
in_file_hv	        ：災害後SARバイナリ(HV偏波)データ（*.mgp_HVm）
in_file_vv	        ：災害後SARバイナリ(VV偏波)データ（*.mgp_VVm）
in_file_info	    ：災害後諸元データ（*.mgp_HHm）
out_path	        ：出力ディレクトリ
filter_size_az	    ：マルチルックサイズ（アジマス方向）
filter_size_gr	    ：マルチルックサイズ（グランドレンジ方向）


3.土砂崩れ領域画像の生成

コマンド：python3.6 extract_landslide_area.py in_file_before in_file_after out_path [--threshold THRESHOLD] [--filter_size FILTER_SIZE FILTER_SIZE]

in_file_before		：災害前単偏波合成(RGB)画像（*.tif）
in_file_after		：災害後単偏波合成(RGB)画像（*.tif）
out_path	        ：出力ディレクトリ
THRESHOLD	        ：閾値　⇒　[0 255] （0（デフォルト）：大津の二値化）
FILTERSIZE	        ：フィルタリングサイズ

 
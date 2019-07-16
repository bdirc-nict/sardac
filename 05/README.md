
マップ      ：二次避難・物資輸送ルートマップ
対象        ：東日本大震災（仙台空港付近データ）
入力データ  ：
    災害後SARバイナリ（HH偏波）データ   ：Sendai01.mgp_HHm
    災害後SARバイナリ（HV偏波）データ   ：Sendai01.mgp_HVm
    災害後SARバイナリ（VV偏波）データ   ：Sendai01.mgp_VVm
    諸元データ                          ：Sendai01.mgp_HHm_info
    数値標高ファイル                    ：sendai_dem.shp
    マスクデータ                        ：マスクデータ.shp
    

1.単偏波合成画像の生成

コマンド：python3.6 create_comp_image.py in_file_hh in_file_hv in_file_vv in_file_info out_path filter_size_az filter_size_gr

in_file_hh	    ：災害後SARバイナリ(HH偏波)データ（*.mgp_HHm）
in_file_hv	    ：災害後SARバイナリ(HV偏波)データ（*.mgp_HVm）
in_file_vv	    ：災害後SARバイナリ(VV偏波)データ（*.mgp_VVm）
in_file_info	：災害後諸元データ（*.mgp_HHm）
out_path	    ：出力ディレクトリ
filter_size_az	：マルチルックサイズ（アジマス方向）
filter_size_gr	：マルチルックサイズ（グランドレンジ方向）


2.浸水領域画像の生成

コマンド：python3.6 extract_flooded_area.py in_file out_path [--threshold THRESHOLD] [--filter_size FILTER_SIZE FILTER_SIZE]

in_file		    ：災害後単偏波合成(RGB)画像（*.tif）
out_path	    ：出力ディレクトリ
THRESHOLD	    ：閾値　⇒　[0 255] （0（デフォルト）：大津の二値化）
FILTERSIZE	    ：フィルタリングサイズ


3.ラスタベクタ変換

コマンド：python3.6 trans_vector.py in_file out_path dem_file type [--non_damaged flg]

in_file         ：浸水領域画像（*.tif）
out_path        ：出力ディレクトリ
dem_file        ：数値標高ファイル（*.shp）
type            ：flood
flg             ：被害領域※　⇒　0
※ 浸水領域画像（0：非被害領域、255：被害領域）から被害領域を対象にベクタ変換を行う


4.浸水領域マスクデータによるフィルタリング

コマンド：python3.6 clip_shape.py in_mesh in_mask out_path --pick_not_contain

in_mesh         ：浸水領域ベクタ（*.shp）
in_mask         ：マスクベクタ（ポリゴン）データ（data/浸水域外.shp）
out_path        ：出力ディレクトリ



 

マップ      ：危険木マップ
対象        ：熊本地震（阿蘇大橋付近データ）
入力データ  ：
    災害前SARバイナリ（HH偏波）データ   ：Obs15_00-04.mgp_HHm
    災害前SARバイナリ（HV偏波）データ   ：Obs15_00-04.mgp_HVm
    災害前SARバイナリ（VV偏波）データ   ：Obs15_00-04.mgp_VVm
    災害前諸元データ                    ：Obs15_00-04.mgp_HHm_info
    災害後SARバイナリ（HH偏波）データ   ：Obs09_00-04.mgp_HHm
    災害後SARバイナリ（HV偏波）データ   ：Obs09_00-04.mgp_HVm
    災害後SARバイナリ（VV偏波）データ   ：Obs09_00-04.mgp_VVm
    災害後諸元データ                    ：Obs09_00-04.mgp_HHm_info
    数値標高ファイル                    ：kumamoto_dem.shp
    教師データ                          ：教師データ.shp
    決定木データ                        ：決定木データ.csv
    

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

コマンド：python3.6 extract_land_slide_area.py in_file_before in_file_after out_path [--threshold THRESHOLD] [--filter_size FILTER_SIZE FILTER_SIZE]

in_file_before		：災害前単偏波合成(RGB)画像（*.tif）
in_file_after		：災害後単偏波合成(RGB)画像（*.tif）
out_path	        ：出力ディレクトリ
THRESHOLD	        ：閾値　⇒　0：大津の二値化
FILTERSIZE	        ：1

4.ラスタベクタ変換（土砂崩れ領域）

コマンド：python3.6 trans_vector.py in_file out_path dem_file landslide

in_file             ：土砂崩れ領域画像（*.tif）
out_path            ：出力ディレクトリ
dem_file            ：数値標高ファイル（*.shp）


5.表面散乱(Ps)画像（災害後）の生成
    
コマンド：python3.6 create_four_comp.py in_file_hh in_file_hv in_file_vv in_file_info out_path filter_size_az filter_size_gr

in_file_hh	        ：災害前SARバイナリ(HH偏波)データ（*.mgp_HHm）
in_file_hv	        ：災害前SARバイナリ(HV偏波)データ（*.mgp_HVm）
in_file_vv	        ：災害前SARバイナリ(VV偏波)データ（*.mgp_VVm）
in_file_info	    ：災害前諸元データ（*.mgp_HHm）
out_path	        ：出力ディレクトリ
filter_size_az	    ：マルチルックサイズ（アジマス方向）
filter_size_gr	    ：マルチルックサイズ（グランドレンジ方向）


6.オブジェクト分類

・eCognition(有償ソフト）※により教師データ（空中写真から判読した斜木等のサンプルデータ）から
オブジェクト分類を実施
※http://www.infoserve.co.jp/Trimble/eCognition_Developer.html

    出力結果：data/output/オブジェクト分類後データ.shp


7.土砂崩れ領域によるフィルタリング

コマンド：python3.6 clip_shape.py in_mesh in_mask out_path

in_mesh         ：オブジェクト分類後ベクタ（*.shp）
in_mask         ：土砂崩れ領域ベクタデータ（*.shp）
out_path        ：出力ディレクトリ

    出力結果：data/output/斜め木.shp
    

8.決定木解析

・崩壊地と斜木を分けるための決定木解析を行うため、Rスクリプト※を実行

※Rのインストールが必要
https://qiita.com/daifuku_mochi2/items/ad0b398e6affd0688c97

    スクリプト：rpart.R
    入力データ：data/input/決定木データ.csv

    
9.斜木と崩壊地の分類

・オブジェクト分類後の「GLCM_Homog_3」の値が0.07以上か未満かで斜木と崩壊地を分類


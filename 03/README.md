
マップ      ：複合災害マップ
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
    数値標高ファイル                    ：kumamoto_dem.shp
    GIS道路データ                       ：kumamoto_road.shp
    

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
THRESHOLD	        ：閾値　⇒　[0 255] （0（デフォルト）：大津の二値化）
FILTERSIZE	        ：フィルタリングサイズ


4.ラスタベクタ変換（土砂崩れ領域）

コマンド：python3.6 trans_vector.py in_file out_path dem_file landslide

in_file             ：土砂崩れ領域画像（*.tif）
out_path            ：出力ディレクトリ
dem_file            ：数値標高ファイル（*.shp）


5.GIS道路データよるフィルタリング

コマンド：python3.6 clip_shape.py in_mesh in_mask out_path

in_mesh         ：土砂崩れ領域ベクタ（*.shp）
in_mask         ：ＧＩＳ道路データ（data/input/kumamoto_road.shp）
out_path        ：出力ディレクトリ


6.孤立道路ＮＷの探索

コマンド：createIsolatedRoadMap.py in_file_osm in_file_grid ot_file_allHighway ot_file_cutNodes ot_file_cutHighway ot_file_notIsolatedHighway ot_file_allNodes ot_file_isolatedNodes
                                
in_file_osm                 ：osmファイル（dara/osm/kumamoto_small.osm）
in_file_grid                ：GIS道路データによるフィルタリング後ベクタデータ（*.shp）
ot_file_allHighway          ：道路データ名(*.shp)完全パス
ot_file_cutNodes            ：グリッドによって寸断されたconnection両端のノード(*.shp)完全パス
ot_file_cutHighway          ：グリッドによって寸断された道路データ(*.shp)完全パス
ot_file_notIsolatedHighway  ：孤立した経路を削除した道路ＮＷエッジ名(*.shp)完全パス
ot_file_allNodes            ：道路構成ノード名(*.shp)完全パス
ot_file_isolatedNodes       ：孤立した道路ＮＷノード(*.shp)完全パス


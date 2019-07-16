
マップ      ：農地の被害状況の把握マップ
対象        ：東日本大震災（仙台空港付近データ）
入力データ  ：
    災害後SARバイナリ（HH偏波）データ   ：Sendai01.mgp_HHm
    災害後SARバイナリ（HV偏波）データ   ：Sendai01.mgp_HVm
    災害後SARバイナリ（VV偏波）データ   ：Sendai01.mgp_VVm
    諸元データ                          ：Sendai01.mgp_HHm_info
    数値標高ファイル                    ：sendai_dem.shp
    

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


3.ラスタベクタ変換（被害領域）

コマンド：python3.6 trans_vector.py in_file out_path dem_file flood

in_file         ：浸水領域画像（*.tif）
out_path        ：出力ディレクトリ
dem_file        ：数値標高ファイル（*.shp）


4.ラスタベクタ変換（非被害領域）

コマンド：python3.6 trans_vector.py in_file out_path --non_damaged dem_file flood

in_file         ：浸水領域画像（*.tif）
out_path        ：出力ディレクトリ
dem_file        ：数値標高ファイル（*.shp）


5.浸水領域の再抽出（標高フィルタ）

コマンド：python3.6 clip_value.py in_file out_path min_height max_height

in_file         ：非浸水抽出ベクタ（*.shp）
out_path        ：出力ディレクトリ
min_height      ：-1
max_height      ：2.5


6.浸水領域の画像化

・3.、5.で抽出した浸水領域ベクタを画像変換する（ピクセル値は標高）

    出力結果：data/output/浸水領域画像(標高フィルタ).tif


7.体積散乱(Pv)画像の生成

コマンド：python3.6 create_four_comp.py in_file_hh in_file_hv in_file_vv in_file_info out_path filter_size_az filter_size_gr

in_file_hh	        ：災害前SARバイナリ(HH偏波)データ（*.mgp_HHm）
in_file_hv	        ：災害前SARバイナリ(HV偏波)データ（*.mgp_HVm）
in_file_vv	        ：災害前SARバイナリ(VV偏波)データ（*.mgp_VVm）
in_file_info	    ：災害前諸元データ（*.mgp_HHm）
out_path	        ：出力ディレクトリ
filter_size_az	    ：マルチルックサイズ（アジマス方向）
filter_size_gr	    ：マルチルックサイズ（グランドレンジ方向）


8.瓦礫の抽出

・教師付き分類を用い、瓦礫を抽出する

    入力データ：体積散乱（Pv）画像
    教師データ：data/input/教師データ.shp
        ガレキ：
            Google Earthで災害当時の衛星画像を見ながら、ガレキであると思われる地点をサンプリング
        
    出力結果：
        ラスタ：data/output/瓦礫画像.tif
        ベクタ：data/output/瓦礫領域.shp



9.圃場ポリゴンの空間結合

・圃場ポリゴンに浸水域の有無・標高平均を空間結合にて算出した結果
※浸水域のデータは、3.、5.のポリゴン データを使用

    出力結果：data/output/浸水領域（農地）.shp
    
・圃場ポリゴンに抽出したガレキの有無・総面積を空間結合にて算出した結果
※ガレキのデータは、瓦礫画像.shp を使用

    出力結果：data/output/瓦礫領域（農地）.shp
    


10.出力結果をWeb可視化ソフトで閲覧

・docs/アークチーム補足資料_アプリ説明.pdfを参照



 
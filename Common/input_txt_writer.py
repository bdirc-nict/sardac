# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: input_txt_writer.py
# Creation date	: March 18, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

from os import path

"""
SAR分析チャレンジ ハンズオン

登録するラスタ・ベクタデータの災害種類番号を定義します

"""
dic_data_type = {
    1: "土砂",
    2: "浸水",
}

"""
SAR分析チャレンジ ハンズオン

登録するラスタ・ベクタデータの種類番号を定義します

"""
dic_image_type = {
    4: "単偏波合成画像(災害前)",
    5: "単偏波合成画像(災害後)",
    6: "四成分合成画像(災害前)",
    7: "四成分合成画像(災害後)",
    8: "パウリ合成画像(災害前)",
    9: "パウリ合成画像(災害後)",
    10: "差分ポリゴンShapeFile",
    11: "差分画像",
    12: "ｵﾘｼﾞﾅﾙ(災害前)",
    13: "ｵﾘｼﾞﾅﾙ(災害後)",
}

"""
SAR分析チャレンジ ハンズオン

登録するラスタ・ベクタデータの観測エリア番号を定義します

"""
dic_area_type = {
    2: "東北",
    9: "九州",
}


class InputTxtData:
    """
    "input.txt" data
    """
    def __init__(self):
        self.time_str = ""
        self.data_type_id = 0
        self.image_type_id = 0
        self.area_type_id = 0
        self.title = ""
        self.mode = ""
        self.survey_area = ""
        self.aircraft_height = ""
        self.aircraft_direction = ""
        self.term_from = ""
        self.term_to = ""
        self.image_date = ""

    @staticmethod
    def create_flood_data(time_str, image_type_id):
        """
        SAR分析チャレンジ ハンズオン

        浸水領域として登録するラスタ・ベクタデータの情報を定義します

        関数：create_flood_data
        引数1：データのID
        引数2：ラスタ・ベクタデータの種類
        
        返り値：ラスタ・ベクタデータの情報
        """
        
        
        
        """
        data                    ：ラスタ・ベクタデータの情報インスタンス
        data.time_str           ：データのID
        data.data_type_id       ：被災種類-->2(浸水)で固定
        data.image_type_id      ：ラスタ・ベクタデータの種類
        data.area_type_id       ：観測エリア-->2(東北)で固定
        data.title              ：データのタイトル
        data.mode               ：SARデータ取得モード--><Mode1で固定
        data.survey_area        ：観測領域
        data.aircraft_height    ：飛行高度
        data.aircraft_direction ：観測方向
        data.term_from          ：災害発生時間(開始)-->20110311で固定
        data.term_to            ：災害発生時間(終了)-->20110311で固定
        data.image_date         ：観測日時-->20110318で固定
        """
        data = InputTxtData()
        data.time_str = time_str
        data.data_type_id = 2
        data.image_type_id = image_type_id
        data.area_type_id = 2
        data.title = "東日本大震災浸水領域"
        data.mode = "Mode1"
        data.survey_area = "仙台市仙台空港付近"
        data.aircraft_height = ""
        data.aircraft_direction = ""
        data.term_from = "20110311"
        data.term_to = "20110311"
        data.image_date = "20110318"
        return data

    @staticmethod
    def create_land_slide_data(time_str, image_type_id, image_date):
        """
        SAR分析チャレンジ ハンズオン
        
        土砂崩れ領域として登録するラスタ・ベクタデータの情報を定義します

        関数：create_land_slide_data
        引数1：データのID
        引数2：ラスタ・ベクタデータの種類
        引数3：観測日時
        
        返り値：ラスタ・ベクタデータの情報
        """
        
        
        
        """
        data                    ：ラスタ・ベクタデータの情報インスタンス
        data.time_str           ：データのID
        data.data_type_id       ：被災種類-->1(土砂崩れ)で固定
        data.image_type_id      ：ラスタ・ベクタデータの種類
        data.area_type_id       ：観測エリア-->9(九州)で固定
        data.title              ：データのタイトル
        data.mode               ：SARデータ取得モード--><Mode1で固定
        data.survey_area        ：観測領域
        data.aircraft_height    ：飛行高度
        data.aircraft_direction ：観測方向
        data.term_from          ：災害発生時間(開始)-->20160414で固定
        data.term_to            ：災害発生時間(終了)-->20160414で固定
        data.image_date         ：観測日時
        """
        data = InputTxtData()
        data.time_str = time_str
        data.data_type_id = 1
        data.image_type_id = image_type_id
        data.area_type_id = 9
        data.title = "熊本地震土砂崩れ領域"
        data.mode = "Mode1"
        data.survey_area = "熊本市阿蘇大橋付近"
        data.aircraft_height = ""
        data.aircraft_direction = ""
        data.term_from = "20160414"
        data.term_to = "20160414"
        data.image_date = image_date
        return data

    def write_file(self, ot_dir):
        """
        Write "input.txt".
        :param ot_dir: output path
        """
        ot_file = path.join(ot_dir, "input.txt")
        writer = open(ot_file, "w", encoding="utf-8")
        writer.writelines([line + "\n" for line in self.create_lines()])

    def create_lines(self):
        """
        Create data record of output data.
        :return: list of record
        """
        id_str = "{0}_{1}{2:02}".format(self.time_str, self.data_type_id, self.image_type_id)
        return [
            id_str,
            str(self.data_type_id),
            dic_data_type[self.data_type_id],
            str(self.image_type_id),
            dic_image_type[self.image_type_id],
            str(self.area_type_id),
            dic_area_type[self.area_type_id],
            self.title,
            self.mode,
            self.survey_area,
            self.aircraft_height,
            self.aircraft_direction,
            self.term_from,
            self.term_to,
            id_str,
            self.image_date,
        ]
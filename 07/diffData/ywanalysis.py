import numpy as np
from os import path
#from create_comp_image import exband_histgram
from Common.constant import DEV_FLAG, DATA_PATH_BASE, IMAGE_FLOAT


#ヒストグラムをファイル出力
def saveHistogram(path, ohist):
    f = open(path, mode='w')

    for i in range(len(ohist[0])):
        #s = str(1.0 / 90.0)* i + ' ' + str(ohist[0][i]) + ' ' + str(ohist[1][i]) + '\n'
        s = str(i) + ' ' + str(ohist[0][i]) + ' ' + str(ohist[1][i]) + '\n'
     
        f.write(s)

    f.close()

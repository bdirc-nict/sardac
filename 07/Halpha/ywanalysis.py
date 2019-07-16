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

#画像出力のために8bit範囲に変換する 標準偏差補正は外す
def exband2Range(src_matrix, min_value, max_value):
    """
    オンライン学習１　SAR画像解析基礎編
    
    画像の色調補正を行います
    
    関数   ： exband_histgram
    引数1  ： SARデータ2次元配列
    
    """
    # replace inf and nan with 0
    src_matrix = np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    #min_value = src_matrix.min()
    #max_value = src_matrix.max()
    #min_value = -94.0
    #max_value = 67
    print("min max-")
    print(src_matrix.min())
    print(src_matrix.max())
    if min_value < 0 :
        print("minval minus")
        print (min_value)
        
    min_result = 10
    max_result = 245

    # convert from min_result to max value
    grad = (max_result - min_result) / (max_value - min_value)
    intercept = min_result - min_value * grad
    src_matrix = src_matrix * grad + intercept
    
    # convert standard deviation
    #src_matrix = (src_matrix - src_matrix.mean()) / src_matrix.std() * 50 + src_matrix.mean()

    src_matrix[src_matrix < min_result] = min_result
    src_matrix[src_matrix > max_result] = max_result
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    if IMAGE_FLOAT:
        return src_matrix.astype(np.float32)
    else:
        return src_matrix.astype(np.uint8)

def exband2RangeMag(src_matrix, min_value, max_value, mag):
    """
    オンライン学習１　SAR画像解析基礎編
    
    画像の色調補正を行います
    
    関数   ： exband_histgram
    引数1  ： SARデータ2次元配列
    
    """
    # replace inf and nan with 0
    src_matrix = np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    #min_value = src_matrix.min()
    #max_value = src_matrix.max()
    #min_value = -94.0
    #max_value = 67
    print("min max-")
    print(src_matrix.min())
    print(src_matrix.max())
    if min_value < 0 :
        print("minval minus")
        print (min_value)
        
    min_result = 10
    max_result = 245

    # convert from min_result to max value
    grad = (max_result - min_result) / (max_value - min_value)
    intercept = min_result - min_value * grad
    src_matrix = src_matrix * grad + intercept
    
    src_matrix = src_matrix * mag
    # convert standard deviation
    #src_matrix = (src_matrix - src_matrix.mean()) / src_matrix.std() * 50 + src_matrix.mean()

    src_matrix[src_matrix < min_result] = min_result
    src_matrix[src_matrix > max_result] = max_result
    np.vectorize(lambda x: x if (np.isfinite(x) and not np.isnan(x)) else 0)(src_matrix)

    if IMAGE_FLOAT:
        return src_matrix.astype(np.float32)
    else:
        return src_matrix.astype(np.uint8)

def entropyAlpha(entropy, alpha):
    out = []
    
    for i in range(9):
        out.append(np.zeros(entropy.shape,dtype=np.float32))
    
    #out = entropy.all()
    #out.any()[0.5 < entropy < 0.88 & alpha > 50.0] = 250
    print(entropy.shape)
    print (alpha.shape)
    
    print(out[0].shape[0])
    
    print(entropy.min())
    print(entropy.max())
    print(alpha.min())
    print(alpha.max())
    
    alphadeg = (alpha * 180.0 / np.pi).real
    print(alphadeg.min())
    print(alphadeg.max())
    
    #plt.hist(entropy, 100)
    tmpEnt = entropy.real
    
    #oHhist = np.histogram(tmpEnt, 100) #, range=None, normed=False, weights=None, density=None)
    #ohist = np.histogram(alphadeg, 90) #, range=None, normed=False, weights=None, density=None)
    
    #path = '/mnt/nfsdir/usr4/workspace/output/alphahist.txt'
    path = '/mnt/nfsdir/usr4/workspace/output/enthist.txt'
    #saveHistogram(path, oHhist)
    
    #oHhistNormalize = np.histogram(exband_histgramT(tmpEnt), 100)
    #saveHistogram('/mnt/nfsdir/usr4/workspace/output/entNormalizehist.txt', oHhistNormalize)
    
    for j in range(out[0].shape[1]):
        for i in range(out[0].shape[0]):
            if(0.5 >  entropy[i][j].real):
                if alphadeg[i][j] > 48.0:
                    out[7][i][j] = 240
                elif alphadeg[i][j] > 42.0:
                    out[8][i][j] = 240
                else:
                    out[0][i][j] = 240
                
            elif entropy[i][j].real < 0.88:
                if alphadeg[i][j] > 50.0:
                    out[4][i][j] = 240
                elif alphadeg[i][j] > 40.0:
                    out[5][i][j] = 240
                else:
                    out[6][i][j] = 240
                
            else:#    ) and (alpha[i][j] > 50.0):
                if alphadeg[i][j] > 53.0:
                    out[1][i][j] = 240.0
                elif alphadeg[i][j] > 40.0:
                    out[2][i][j] = 240.0
                else:
                    out[3][i][j] = 240.0


    for i in range(9):
        out[i] = out[i].astype(np.uint8)
    # out[1].astype(np.uint8)
    # out[2].astype(np.uint8)
    # out[3].astype(np.uint8)
    # out[4].astype(np.uint8)
    # out[5].astype(np.uint8)
    # out[6].astype(np.uint8)
    # out[7].astype(np.uint8)
    # out[8].astype(np.uint8)
    
    return out
    

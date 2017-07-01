#coding= utf-8
import codecs
import sys
import RecordFunction
import MysqlManager
import os


#main関数
#RecordFunction.loadOriginalRaceResultData('K150706.TXT')


targetDir = 'RaceResult/'

fileList =  os.listdir(targetDir)

for fileName in fileList:
    if fileName !=  ".DS_Store":
        try:
            RecordFunction.loadOriginalRaceResultData(targetDir + fileName)
        except:
            print("エラー発生:"+ fileName)
        else:
            print(fileName)
    else:
        print("Not Target File.")


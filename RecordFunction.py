#coding= utf-8
import codecs
import sys
import MysqlManager

TANSHO = 1
HUKUSHO = 2
NIRENTAN = 3
NIRENPUKU = 4
KAKURENPUKU = 5
SANRENTAN = 6
SANRENPUKU = 7


def loadOriginalRaceResultData(fileName):
    dBManager = MysqlManager.DBManager()
    #絶対行。ログ吐き出しにしか使わない。
    absoluteRow = 0
    #内部のデータを読み取る時の基準に使用する行
    relativeRow = 1
    startRoundRow = 0
    MIN_RELATIVE_START_1R_ROW = 27

    #レース名
    raceName = ""
    for line in codecs.open(fileName,'r','shift_jis'):
        absoluteRow += 1
        relativeRow += 1
        #print(str(absoluteRow) + '行目')

        if 'STARTK' in line:
            continue

        if 'KEND' in line:
            continue

        if 'KBGN' in line:
            relativeRow = 0
            betType = 0
            courseName = ''
            continue

        if(relativeRow == 1):
            courseName = splitRecord(line,[3])[0]

        if(relativeRow == 5):
            raceName = line

        if(relativeRow == 7):
            raceCourseInfo = splitRaceTitleInfo(line)
            dBManager.defineSituationData(raceCourseInfo[2],courseName,raceName)

        if(relativeRow < MIN_RELATIVE_START_1R_ROW):
            continue

        if(isRoundStart(line) == True):
            startRoundRow = relativeRow
            conditionList = splitRaceConditionInfo(line)
            dBManager.setRound(conditionList[0])
            dBManager.insertCourseCondition(conditionList)

        elif(relativeRow >= (startRoundRow + 3) and
                     relativeRow <= (startRoundRow + 3 + 5)):
            racerResult = splitRacerRecord(line)
            del racerResult[3]
            dBManager.insertRacerRecord(racerResult)

        elif(relativeRow > (startRoundRow + 3 + 6)):
            resultBetType = checkBetType(line)
            if(resultBetType != -1):
                betType = resultBetType

            raceResultRecord = splitRaceResult(line,betType,resultBetType)

            #不成立の場合は記録しない
            if raceResultRecord == -1:
                continue
            #レース不成立の場合、オッズ結果の行が存在しないため、行を進める。
            if raceResultRecord == -2:
                relativeRow += 11
                continue

            #MySQLManager 結果レコードを登録する処理を実行する。
            if betType == HUKUSHO:
                #ここは2回分
                dBManager.insertRaceResult(raceResultRecord[0])
                if raceResultRecord[1][4].strip() != "":
                    dBManager.insertRaceResult(raceResultRecord[1])
            else:
                #ここは1回
                dBManager.insertRaceResult(raceResultRecord)
        else:
            pass

#データを固定長文字で区切って表示する
def splitRecord(racerResult,splitNum):
    resultList = []
    startIndex = 0

    for index in splitNum:
        #resultList.append(racerResult[startIndex:startIndex + index])
        resultList.append(racerResult[startIndex:startIndex + index])
        startIndex += index
    return  resultList

#選手の競争成績を固定長文字で区切って表示する
def splitRacerRecord(racerResult):
    splitNum = [4,3,5,10,3,5,6,4,8,11]
    racerRecordList =  splitRecord(racerResult,splitNum)

    filteredList = [isCompletion(racerRecordList[0]),
        racerRecordList[1],
        racerRecordList[2],
        racerRecordList[3],
        racerRecordList[4],
        racerRecordList[5],
        calcTime(racerRecordList[6]),
        checkStartTiming(racerRecordList[7]),
        calcTime(racerRecordList[8]),
        calcRaceTime(racerRecordList[9])]
    return filteredList

#レース結果を固定長文字で区切って表示する
#betType = 元データの結果行を相対行で表しているもの。
#単勝、0行目、複勝、1行目等
def splitRaceResult(resultStr,betType,resultBetType):
    if u'レース不成立' in resultStr:
        return -2
    if u'不成立' in resultStr:
        return -1
    if u'特払い' in resultStr:
        return -1
    if resultStr.strip() == '':
        return -1

    resultList = []
    splitNum = []
    if betType == TANSHO:
        splitNum = [14,8,9]
    elif betType == HUKUSHO:
        splitNum = [14,8,9,8,8]
    elif betType == SANRENTAN or betType == SANRENPUKU:
        if(resultBetType != -1):
            splitNum = [14,6,8,8,7]
        else:
            splitNum = [16,6,9,8,7]
    else:
        if(resultBetType != -1):
            splitNum = [12,8,9,8,7]
        else:
            splitNum = [12,8,11,6,7]

    resultList = splitRecord(resultStr,splitNum)

    if resultList[1].strip() == '':
        return -1

    winList = resultList[1].split("-")

    if betType == TANSHO:
        winnerNum = winList[0]
        if winnerNum.strip().isdigit() == False:
            winnerNum = 7
        resultList = [betType,
                        winnerNum,
                        0,
                        0,
                        resultList[2],
                        0
                        ]
    elif betType == HUKUSHO:
        winnerNum = winList[0]
        firstRate = resultList[2]
        secondRate = resultList[4]
        if firstRate.strip().isdigit() == False:
            firstRate = '0'
        if secondRate.strip().isdigit() == False:
            secondRate = '0'
        if winnerNum.strip().isdigit() == False:
            winnerNum = 7
            resultList = [[betType,winnerNum,0,0,firstRate,0],
                         [betType,winnerNum,0,0,secondRate,0],
                        ]
        else:
            resultList = [[betType,resultList[1],0,0,resultList[2],0],
                         [betType,resultList[3],0,0,resultList[4],0],
                        ]
    elif betType == NIRENTAN or betType == NIRENPUKU or betType == KAKURENPUKU:
        resultList = [betType,
                        winList[0],
                        winList[1],
                        0,
                        resultList[2],
                        resultList[4],
                        ]
    elif betType == SANRENTAN or betType == SANRENPUKU:
        resultList = [betType,
                        winList[0],
                        winList[1],
                        winList[2],
                        resultList[2],
                        resultList[4],
                        ]
    return resultList

#レース場の天候データなどを固定長文字で区切って表示する
def splitRaceConditionInfo(infoStr):
    if u"進入固定" in infoStr:
        splitNum = [5,26,6,5,3,4,4,5,8]
    else:
        splitNum = [5,30,6,5,3,4,4,5,8]
    conditionList =  splitRecord(infoStr,splitNum)

    filteredList = [trimSplitedData(conditionList[0]),
                    trimSplitedData(conditionList[2],LTrimNum=1),
                    convWeatherCharToInt(conditionList[3]),
                    convDirCharToInt(conditionList[5]),
                    trimSplitedData(conditionList[6]),
                    trimSplitedData(conditionList[8],RTrimNum=2)]

    return filteredList

#年月日、レース場名などを固定長文字で区切って表示する
def splitRaceTitleInfo(infoStr):
    splitNum = [5,4,20,30,12]
    return splitRecord(infoStr,splitNum)


#分割してリストに入れたデータにある、余計なスペースと末尾にある余計な文字を削る
def trimSplitedData(data,LTrimNum=0,RTrimNum=1):
    data = str(data)
    data = data.strip()
    if LTrimNum > 0:
        data = data[LTrimNum:]
    data = data[:RTrimNum * -1]
    #data = int(data)
    data = data.strip()
    return data

def convDirCharToInt(dirChar):
    #無風
    dirChar = dirChar.strip()
    retValue = 0
    if dirChar == u"北":
        retValue = 1
    if dirChar == u"北西":
        retValue = 2
    if dirChar == u"西":
        retValue = 3
    if dirChar == u"南西":
        retValue = 4
    if dirChar == u"南":
        retValue = 5
    if dirChar == u"南東":
        retValue = 6
    if dirChar == u"東":
        retValue = 7
    if dirChar == u"北東":
        retValue = 8

    return retValue

def convWeatherCharToInt(weatherChar):
    weatherChar = weatherChar.strip()
    #不明
    retValue = 0
    if weatherChar == u"晴":
        retValue = 1
    if weatherChar == u"曇り":
        retValue = 2
    if weatherChar == u"雨":
        retValue = 3

    return retValue

def convbetTypeCharToInt(betTypeChar):
    betTypeChar = betTypeChar.strip()
    #不明
    retValue = 0
    if betTypeChar == u"単勝":
        retValue = 1
    if betTypeChar == u"複勝":
        retValue = 2
    if betTypeChar == u"２連単":
        retValue = 3
    if betTypeChar == u"拡連複":
        retValue = 4
    if betTypeChar == u"３連単":
        retValue = 5
    if betTypeChar == u"３連複":
        retValue = 6
    return retValue

def convfinishCharToInt(finishChar):
    finishChar = finishChar.strip()
    #不明
    retValue = 0
    if finishChar == u"逃げ":
        retValue = 1
    if finishChar == u"差し":
        retValue = 2
    if finishChar == u"捲り":
        retValue = 3
    if finishChar == u"抜き":
        retValue = 4
    if finishChar == u"繰上":
        retValue = 5
    return retValue

def calcTime(startTime):
    if startTime.strip().replace(".","").isdigit() == False:
        return 9999.9
    else:
        return startTime

def calcRaceTime(raceTime):
    retValue = 0
    splitRaceTimeList = raceTime.split(".")
    if len(splitRaceTimeList) <= 2:
        return 9999.9
    if splitRaceTimeList[0].strip().isdigit() == False:
        return 9999.9
    retValue =  float(splitRaceTimeList[0]) * 60
    retValue+= float(splitRaceTimeList[1])
    retValue+= float(splitRaceTimeList[2]) * 0.1
    return retValue


def isCompletion(arrival):
    if arrival.strip() == "S0":
        return 7
    elif arrival.strip() == "S1":
        return 8
    elif arrival.strip() == "S2":
        return 9
    elif arrival.strip() == "F":
        return 10
    elif arrival.strip() == "L0":
        return 11
    elif arrival.strip() == "L1":
        return 12
    elif arrival.strip() == "K0":
        return 13
    elif arrival.strip() == "K1":
        return 14
    else:
        return arrival


def checkStartTiming(startTimingNum):
    if startTimingNum.strip().isdigit() == False:
        return 7
    else:
        return startTimingNum

def checkBetType(line):
    if u'単勝' in line:
        return 1
    if u'複勝' in line:
        return 2
    if u'２連単' in line:
        return 3
    if u'２連複' in line:
        return 4
    if u'拡連複' in line:
        return 5
    if u'３連単' in line:
        return 6
    if u'３連複' in line:
        return 7
    else:
        return -1


def isRoundStart(line):
    if '1R' in line:
        return True
    if '2R' in line:
        return True
    if '3R' in line:
        return True
    if '4R' in line:
        return True
    if '5R' in line:
        return True
    if '6R' in line:
        return True
    if '7R' in line:
        return True
    if '8R' in line:
        return True
    if '9R' in line:
        return True
    if '10R' in line:
        return True
    if '11R' in line:
        return True
    if '12R' in line:
        return True
    else:
        return False
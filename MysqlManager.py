#coding=utf-8

import MySQLdb

class DBManager(object):
    #一旦 connector を close したとき用。初回は実行する必要ない。
    def dBConnection(self):
        if self.connector.status == 0:
            connector = MySQLdb.connect(host="localhost",
                                        db="BoatRace" ,
                                        user="root",
                                        passwd="5N4F8uClUSLlGrMM",
                                        charset="utf8")

    connector = MySQLdb.connect(host="localhost",
                                        db="BoatRace" ,
                                        user="root",
                                        passwd="5N4F8uClUSLlGrMM",
                                        charset="utf8")

    raceDate = '2000/01/01'
    courseID = 1
    raceTitleID = 1
    round = 1

    def defineSituationData(self,raceDate,courseName,raceTitleName):
        self.raceDate = "/".join([x.strip() for x in raceDate.split("/")])
        self.courseID = self.selectCourseIDFromName(courseName.strip())
        self.raceTitleID = self.selectRaceTitleIDFromName(raceTitleName.strip())

    def setRound(self,round):
        self.round = round

    def __new__(conn):
        if not hasattr(conn, "__instance__"):
            conn.__instance__ = super(DBManager, conn).__new__(conn)
        return conn.__instance__



    def insertRacerRecord(self,recordDataList):
        kOrderArrival = 0
        kBibs = 1
        kRacerID = 2
        kMotorID = 3
        kBoatID = 4
        kDemoTime = 5
        kBoatEntry = 6
        kStartingTiming = 7
        kRaceTime = 8

        if self.raceTitleID == 0:
            print("error")

        cursor = self.connector.cursor()
        sql = u"INSERT INTO racerRecord(raceDate,courseID,raceTitleID,round,orderArrival,bibs,racerID,motorID,boatID,demoTime,boatEntry,startTiming,raceTime)"
        sql += u"VALUES("
        sql += self.generateQueryItem(self.raceDate,quoteFlag=True)
        sql += self.generateQueryItem(self.courseID)
        sql += self.generateQueryItem(self.raceTitleID)
        sql += self.generateQueryItem(self.round)
        sql += self.generateQueryItem(recordDataList[kOrderArrival])
        sql += self.generateQueryItem(recordDataList[kBibs])
        sql += self.generateQueryItem(recordDataList[kRacerID])
        sql += self.generateQueryItem(recordDataList[kMotorID])
        sql += self.generateQueryItem(recordDataList[kBoatID])
        sql += self.generateQueryItem(recordDataList[kDemoTime])
        sql += self.generateQueryItem(recordDataList[kBoatEntry])
        sql += self.generateQueryItem(recordDataList[kStartingTiming])
        sql += self.generateQueryItem(recordDataList[kRaceTime],comma=False)
        sql += u")"

        cursor.execute(sql)

        self.connector.commit()
        cursor.close()

    def insertCourseCondition(self,recordDataList):
        kPhase = 0
        kCourseRange = 1
        kWeather = 2
        kWindDir = 3
        kWaveHeight = 4
        kFinish = 5

        if self.raceTitleID == 0:
            print("error")

        cursor = self.connector.cursor()

        sql = u"INSERT INTO courseCondition(raceDate,courseID,raceTitleID,round,phase,courseRange,weather,windDir,waveHeight,finishID)"
        sql += u"VALUES("
        sql += self.generateQueryItem(self.raceDate,quoteFlag=True)
        sql += self.generateQueryItem(self.courseID)
        sql += self.generateQueryItem(self.raceTitleID)
        sql += self.generateQueryItem(self.round)
        sql += self.generateQueryItem(recordDataList[kPhase])
        sql += self.generateQueryItem(recordDataList[kCourseRange])
        sql += self.generateQueryItem(recordDataList[kWeather])
        sql += self.generateQueryItem(recordDataList[kWindDir])
        sql += self.generateQueryItem(recordDataList[kWaveHeight])
        sql += self.generateQueryItem(recordDataList[kFinish],comma=False)
        sql += u")"

        cursor.execute(sql)

        self.connector.commit()
        cursor.close()

    def insertRaceResult(self,recordDataList):
        kBetType = 0
        kFirstNumber = 1
        kSecondNumber = 2
        kThirdNumber = 3
        kPayout = 4
        kPopularity = 5

        if self.raceTitleID == 0:
            print("error")

        cursor = self.connector.cursor()

        sql = u"INSERT INTO raceResult(raceDate,courseID,raceTitleID,round,betType,firstNumber,secondNumber,thirdNumber,payout,popularity)"
        sql += u"VALUES("
        sql += self.generateQueryItem(self.raceDate,quoteFlag=True)
        sql += self.generateQueryItem(self.courseID)
        sql += self.generateQueryItem(self.raceTitleID)
        sql += self.generateQueryItem(self.round)
        sql += self.generateQueryItem(recordDataList[kBetType])
        sql += self.generateQueryItem(recordDataList[kFirstNumber])
        sql += self.generateQueryItem(recordDataList[kSecondNumber])
        sql += self.generateQueryItem(recordDataList[kThirdNumber])
        sql += self.generateQueryItem(recordDataList[kPayout])
        sql += self.generateQueryItem(recordDataList[kPopularity],comma=False)

        sql += u")"

        cursor.execute(sql)

        self.connector.commit()
        cursor.close()

    def insertRaceTitle(self,courseName):
        cursor = self.connector.cursor()

        sql = u"INSERT IGNORE INTO raceTitleInfo(raceTitleName)"
        sql += u" VALUES('"
        sql +=courseName.strip()
        sql += u"')"

        cursor.execute(sql)

        self.connector.commit()
        cursor.close()


    def selectCourseIDFromName(self,courseName):
        return self.selectIDFromName(u"SELECT * FROM courseBasicInfo WHERE courseName = ",courseName.strip())

    def selectRaceTitleIDFromName(self,raceTitleName):
        retValue =  self.selectIDFromName(u"SELECT * FROM raceTitleInfo WHERE raceTitleName = ",raceTitleName)
        if retValue == 0:
            self.insertRaceTitle(raceTitleName)
            retValue = self.selectIDFromName(u"SELECT * FROM raceTitleInfo WHERE raceTitleName = ",raceTitleName)
            if retValue != 0:
                return  retValue
            else:
                print("error")
        else:
            return retValue

    #これを直接呼ぶ事はしない。
    def selectIDFromName(self,sqlQuery,mame,rowNum = 0):
        #検索結果が0件だったら場合は、0を返す
        retID = 0
        cursor = self.connector.cursor()

        courseName = u"'" + mame + u"'"
        sql = sqlQuery + courseName
        cursor.execute(sql)
        result = cursor.fetchall()

        for row in result:
            retID = row[rowNum]

        cursor.close()
        return retID

    def generateQueryItem(self,string,quoteFlag = False ,comma = True):
        commaChar = u""

        if comma == True:
            commaChar = u","
        if quoteFlag == True:
            return u"'" + str(string) + u"'" + commaChar
        else:
            return str(string) + commaChar

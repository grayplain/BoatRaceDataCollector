# BoatRaceDataCollector

## 何をするツールなのか
BOATEACE 公式サイトから入手できる競争成績データを自動でダウンロードするツールです。  
http://app.boatrace.jp/data/  


## 環境について
* python 3.x 系の環境で動作します。
* システムのライブラリ以外に、pycurl ライブラリが必要です。  
　http://pycurl.io/

## 注意点
ダウンロードできるデータは txtファイルのため、
https://github.com/grayplain/BoatRaceDataStorager  
等で学習データの素材として扱いやすくする必要があります。

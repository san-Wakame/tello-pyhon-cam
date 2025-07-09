# tello-pyhon-cam  
tello-1.pyはTelloの制御コマンド送信機能とカメラ映像表示機能が統合されています。  
tello-2.pyはtello-1.pyの機能+非同期で映像とコマンド入力を並列化がされています。  

＊必要ライブラリ  
pip install opencv-python numpy  

＊コマンド一覧  
takeoff 離陸  
land 着陸  
up X	上にX cm移動（20〜500）  
down X	下にX cm移動（20〜500）  
left X	左にX cm移動（20〜500）  
right X	右にX cm移動（20〜500）  
forward X	前にX cm移動（20〜500）  
back X	後ろにX cm移動（20〜500）  
cw X	時計回りにX度回転（1〜360）  
ccw X	反時計回りにX度回転（1〜360）  
stop	その場で停止（緊急停止ではない）  
flip l	左に宙返り  
flip r	右に宙返り  
flip f	前に宙返り  
flip b	後ろに宙返り  
speed X	移動スピードを X cm/s に設定（10〜100） ※低速20、普通50、高速100  
streamon	映像ストリーミング開始（自動送信済）  
streamoff	映像ストリーミング停止（終了時に自動送信）  
battery?	バッテリー残量（%）  
speed?	現在のスピード  
time?	飛行時間  
wifi?	Wi-Fiの信号強度  
height?	高度  
temp?	温度  
attitude?	姿勢角度  
q（入力）	キーボード入力スレッドを通じて終了  
q（ウィンドウ）	カメラウィンドウ上でqキー押下で終了  

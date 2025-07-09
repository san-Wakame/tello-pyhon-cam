import socket
import threading
import cv2
import time
import numpy as np

# Tello設定
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)
TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111'

# ソケット作成＆バインド（UDP）
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', TELLO_PORT))

# UDPレスポンス受信関数（別スレッドで常時監視）
def udp_receiver():
    while True:
        try:
            response, _ = sock.recvfrom(1518)
            print("Telloからの応答:", response.decode('utf-8'))
        except Exception as e:
            print("受信エラー:", e)
            break

# スレッド起動
recv_thread = threading.Thread(target=udp_receiver)
recv_thread.daemon = True
recv_thread.start()

# --- 初期コマンド送信 ---
def send_command(cmd):
    try:
        sock.sendto(cmd.encode('utf-8'), TELLO_ADDRESS)
    except Exception as e:
        print(f"コマンド送信エラー: {e}")

print("Telloと接続中...")
send_command('command')  # コマンドモード突入
time.sleep(1)

send_command('streamon')  # カメラストリーム開始
time.sleep(2)

# --- カメラ映像の取得 ---
cap = cv2.VideoCapture(TELLO_CAMERA_ADDRESS)

if not cap.isOpened():
    cap.open(TELLO_CAMERA_ADDRESS)

time.sleep(1)

print("操作を開始します。Telloのコマンドを入力してください。")
print("例: takeoff, land, up 50 など")
print("qキーで終了")

# メインループ
try:
    while True:
        # カメラ映像取得・表示
        ret, frame = cap.read()

        if frame is not None and frame.size != 0:
            h, w = frame.shape[:2]
            frame = cv2.resize(frame, (w // 2, h // 2))
            cv2.imshow('Tello Camera View', frame)

        # 入力受付（ノンブロッキング風）
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("終了処理中...")
            break

        # コマンド入力（blockingなのでカメラが止まるが、簡易版として許容）
        if sock.fileno() != -1:  # ソケットが閉じられていない場合のみ
            msg = input()
            if msg.strip().lower() == 'q':
                print("ユーザー終了")
                break
            if msg:
                send_command(msg)

except KeyboardInterrupt:
    print("Ctrl+Cで終了")

# 終了処理
cap.release()
cv2.destroyAllWindows()
send_command('streamoff')
sock.close()

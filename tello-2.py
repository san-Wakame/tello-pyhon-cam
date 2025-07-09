import socket
import threading
import cv2
import time

# Tello設定
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)
TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111'

# ソケット作成＆バインド（UDP）
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', TELLO_PORT))

# --- Telloからの応答受信用スレッド ---
def udp_receiver():
    while True:
        try:
            response, _ = sock.recvfrom(1518)
            print("Telloからの応答:", response.decode('utf-8'))
        except Exception as e:
            print("受信エラー:", e)
            break

# --- ユーザー入力を非同期で処理するスレッド ---
def command_input():
    while True:
        try:
            msg = input()
            if msg.strip().lower() == 'q':
                print("ユーザーによる終了指示")
                global running
                running = False
                break
            elif msg:
                sock.sendto(msg.encode('utf-8'), TELLO_ADDRESS)
        except Exception as e:
            print("入力エラー:", e)
            break

# --- コマンド送信ヘルパー関数 ---
def send_command(cmd):
    try:
        sock.sendto(cmd.encode('utf-8'), TELLO_ADDRESS)
    except Exception as e:
        print(f"コマンド送信エラー: {e}")

# --- 初期セットアップ ---
print("Telloに接続中...")
send_command('command')  # コマンドモード突入
time.sleep(1)

send_command('streamon')  # カメラストリーム開始
time.sleep(2)

# --- スレッド起動 ---
recv_thread = threading.Thread(target=udp_receiver, daemon=True)
recv_thread.start()

input_thread = threading.Thread(target=command_input, daemon=True)
input_thread.start()

# --- カメラ映像表示（メインスレッド） ---
cap = cv2.VideoCapture(TELLO_CAMERA_ADDRESS)
if not cap.isOpened():
    cap.open(TELLO_CAMERA_ADDRESS)
time.sleep(1)

print("コマンドを入力してください（qで終了）")

running = True
while running:
    ret, frame = cap.read()
    if frame is not None and frame.size != 0:
        h, w = frame.shape[:2]
        frame = cv2.resize(frame, (w // 2, h // 2))
        cv2.imshow('Tello Camera View', frame)

    # キー入力での終了も受付（OpenCV側）
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("カメラ側からの終了")
        running = False
        break

# --- 終了処理 ---
cap.release()
cv2.destroyAllWindows()
send_command('streamoff')
sock.close()

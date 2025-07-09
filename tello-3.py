import socket
import threading
import cv2
import time
import tkinter as tk

# Tello設定
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)
TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111'

# ソケット作成＆バインド（UDP）
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', TELLO_PORT))

running = True  # フラグ制御

# --- Telloからの応答受信用スレッド ---
def udp_receiver():
    while running:
        try:
            response, _ = sock.recvfrom(1518)
            print("Telloからの応答:", response.decode('utf-8'))
        except Exception as e:
            print("受信エラー:", e)
            break

# --- ユーザー入力を非同期で処理するスレッド ---
def command_input():
    global running
    while running:
        try:
            msg = input()
            if msg.strip().lower() == 'q':
                print("ユーザーによる終了指示")
                running = False
                break
            elif msg:
                sock.sendto(msg.encode('utf-8'), TELLO_ADDRESS)
        except Exception as e:
            print("入力エラー:", e)
            break

# --- コマンド送信ヘルパー関数 ---
def send_command(cmd):
    global running
    try:
        print(f">>> {cmd}")
        sock.sendto(cmd.encode('utf-8'), TELLO_ADDRESS)
        if cmd == 'q':
            running = False
    except Exception as e:
        print(f"コマンド送信エラー: {e}")

# --- tkinter GUI作成 ---
def create_gui():
    root = tk.Tk()
    root.title("Tello 操作パネル")
    root.geometry("400x550")

    def add_button(label, cmd):
        tk.Button(root, text=label, width=25, height=2, command=lambda: send_command(cmd)).pack(pady=3)

    tk.Label(root, text="【基本操作】").pack()
    add_button("離陸 (takeoff)", "takeoff")
    add_button("着陸 (land)", "land")

    tk.Label(root, text="【宙返り】").pack()
    add_button("前宙 (flip f)", "flip f")
    add_button("後宙 (flip b)", "flip b")
    add_button("左宙 (flip l)", "flip l")
    add_button("右宙 (flip r)", "flip r")

    tk.Label(root, text="【速度切替】").pack()
    add_button("低速 (speed 20)", "speed 20")
    add_button("中速 (speed 50)", "speed 50")
    add_button("高速 (speed 80)", "speed 80")

    tk.Label(root, text="【カメラ制御】").pack()
    add_button("カメラ開始 (streamon)", "streamon")
    add_button("カメラ停止 (streamoff)", "streamoff")

    tk.Label(root, text="【状態取得】").pack()
    add_button("バッテリー (battery?)", "battery?")
    add_button("速度確認 (speed?)", "speed?")
    add_button("高度確認 (height?)", "height?")

    tk.Label(root, text="【緊急操作】").pack()
    add_button("その場停止 (stop)", "stop")
    add_button("緊急停止 (emergency)", "emergency")
    add_button("終了 (q)", "q")

    threading.Thread(target=root.mainloop, daemon=True).start()

# --- 初期セットアップ ---
print("Telloに接続中...")
send_command('command')
time.sleep(1)
send_command('streamon')
time.sleep(2)

# --- GUI起動 ---
create_gui()

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

while running:
    ret, frame = cap.read()
    if frame is not None and frame.size != 0:
        h, w = frame.shape[:2]
        frame = cv2.resize(frame, (w // 2, h // 2))
        cv2.imshow('Tello Camera View', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("カメラ側からの終了")
        running = False
        break

# --- 終了処理 ---
cap.release()
cv2.destroyAllWindows()
send_command('streamoff')
sock.close()

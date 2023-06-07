import time
import tkinter as tk
from threading import Thread
import cv2
import screen_brightness_control as sbc
from PIL import ImageTk, Image


class Peeking_Preventer:
    def __init__(self):
        # 初始化
        self.root = tk.Tk()
        self.root.title("Peeking Prevent")
        self.video_label = None
        self.status_label = None
        self.capture = None
        self.is_detected = False
        self.gui()

    def gui(self):
        # GUI創建
        self.video_label = tk.Label(self.root)
        self.video_label.pack()
        self.status_label = tk.Label(self.root, text="Detecting Peeker...", font=("arial", 16))
        self.status_label.pack(pady=5)
        close_button = tk.Button(self.root, text="Stop", command=self.close_app)
        close_button.pack(pady=5)

    def starter(self):
        # 攝像頭初始化
        self.capture = cv2.VideoCapture(0)
        thread = Thread(target=self.main_frame)
        thread.daemon = True
        thread.start()

        # 開啟 GUI
        self.root.mainloop()

    def main_frame(self):
        while True:
            # 判斷攝像頭是否輸入
            ret, frame = self.capture.read()
            if not ret:
                break

            # 取得 detect_eyes 函式回傳值
            eye_d = self.detect_eyes(frame)
            eyes = len(eye_d)

            # 轉換攝像頭擷取格式來與 Tkinter GUI 連動
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = img.resize((640, 480))
            img = ImageTk.PhotoImage(img)
            self.video_label.configure(image=img)
            self.video_label.image = img

            # 警示判斷式
            if eyes > 3 and not self.is_detected:
                self.is_detected = True
                self.reduced_screenbright()

            elif eyes <= 3 and self.is_detected:
                self.is_detected = False
                self.improve_screenbright()

            time.sleep(0.1)

    @staticmethod
    def detect_eyes(frame):
        # 調用眼睛辨識模型並辨識數量
        eye_catch = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = eye_catch.detectMultiScale(gray, 1.3, 5)
        return eyes

    @staticmethod
    def reduced_screenbright():
        # 調暗螢幕
        notice_when_detected()
        sbc.set_brightness(5)
        time.sleep(3)

    @staticmethod
    def improve_screenbright():
        # 調亮螢幕
        sbc.set_brightness(60)

    def close_app(self):
        # 釋放攝像頭及關閉程序
        if self.capture is not None:
            self.capture.release()
        self.root.destroy()


def notice_when_detected():
    # 窺視警示視窗
    notice_window = tk.Toplevel()
    notice_window.title("Detected!")
    notice_window.geometry("400x50")
    notice_label = tk.Label(notice_window, text="Someone is peeking your screen!", font=("arial", 18))
    notice_label.pack(pady=10)


if __name__ == "__main__":
    app = Peeking_Preventer()
    app.starter()

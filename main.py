import argparse
import time
import math
import customtkinter as ctk
import cv2
import keyboard
import mss
import numpy as np
from ultralytics import YOLO
import win32api
import win32con
from PIL import Image, ImageTk

parser = argparse.ArgumentParser()
parser.add_argument("game", help="Select game", type=int)
args = parser.parse_args()
game = args.game / 10
if args.game == 44:
    trigger = 10
else:
    trigger = 2

hitweak = 25

width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) / 2
height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) / 2
start_time = time.time()
wconst = 640
frame_count = 0
fps = 0
scale = 1
scale_weak = 0.64
target_dist_closest = 9999999
key_pressed1 = False
key_pressed2 = False
own_player = False
half = wconst / 2
screen = mss.mss()
detection_box = {'left': int(width - half), 'top': int(height - half),
                 'width': int(wconst), 'height': int(wconst)}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
root = ctk.CTk()
root.geometry("1000x1000")
root.title("Options")
root.resizable(False, False)

var1 = ctk.IntVar()
checkbox1 = ctk.CTkCheckBox(master=root, text="Softaim", variable=var1)
checkbox1.place(x=10, y=10)

var2 = ctk.IntVar()
checkbox2 = ctk.CTkCheckBox(master=root, text="Triggerbot", variable=var2)
checkbox2.place(x=10, y=35)

img = ctk.CTkLabel(root, image=None, text="")
img.place(x=360, y=360)

label = ctk.CTkLabel(root, text=f"FPS: {fps}", font=("Arial", 40))
label.place(x=360, y=300)

model = YOLO('best.pt')


def keybinds():
    global key_pressed1, key_pressed2
    if keyboard.is_pressed('&') and not key_pressed1:
        checkbox1.toggle()
        key_pressed1 = True
    elif not keyboard.is_pressed('&'):
        key_pressed1 = False
    if keyboard.is_pressed('é') and not key_pressed2:
        checkbox2.toggle()
        key_pressed2 = True
    elif not keyboard.is_pressed('é'):
        key_pressed2 = False


def window(window0):
    img0 = cv2.cvtColor(window0, cv2.COLOR_BGR2RGB)
    img0 = cv2.resize(img0, (640, 640), interpolation=cv2.INTER_AREA)
    img0 = ImageTk.PhotoImage(Image.fromarray(img0))
    img.configure(image=img0)
    label.configure(text=f"FPS: {round(fps)}")


while True:
    root.update()
    keybinds()
    # noinspection PyTypeChecker
    frame = np.array(screen.grab(detection_box))
    window(frame)
    start_time = time.time()
    frame_count = 0
    fps = 0

    while checkbox1.get() == 1:
        root.update()
        keybinds()
        frame_count += 1
        elapsed_time = time.time() - start_time
        if elapsed_time != 0:
            fps = frame_count / elapsed_time
        # noinspection PyTypeChecker
        frame = np.array(screen.grab(detection_box))[:, :, :3]
        results = model.predict(frame, conf=0.4)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        for r in results:
            distances = []
            targets = []
            sort = []
            weak = []
            distances.clear()
            targets.clear()
            sort.clear()
            weak.clear()
            for cls, box in zip(r.boxes.cls, r.boxes.xyxy):
                x1, y1, x2, y2 = map(int, box)
                x = int(((x1 + x2) / 2) - half)
                y = int(((y1 + y2) / 2) - ((y2 - y1) / game) - half)
                weak_y = int(((y1 + y2) / 2) - half)
                dist = math.sqrt(x * x + y * y)
                own_player = x1 < 128 and 220 < y2
                sort.append(round(int(cls)))
                weak.append((x, weak_y))
                distances.append(dist)
                targets.append((x, y))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)

            if len(distances) != 0 and sort[0] == 0:
                min_index = distances.index(min(distances))
                x, y = targets[min_index]

                if win32api.GetKeyState(0x02) in (-127, -128) and not own_player \
                        and not (half - 1 <= x + half <= half + 1 and half - 1 <= y + half <= half + 1):
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x * scale), int(y * scale), 0, 0)

                if win32api.GetKeyState(0x02) in (-127, -128) and not own_player \
                        and half - trigger <= x + half <= half + trigger \
                        and half - trigger <= y + half <= half + trigger \
                        and checkbox2.get() == 1:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                cv2.line(frame, (int(half), int(half)), (x + int(half), y + int(half)), (0, 0, 255), 1)
                cv2.circle(frame, (int(x + half), int(y + half)), 2, (0, 255, 0), -1)

            if len(distances) != 0 and sort[0] == 1:
                min_index = distances.index(min(distances))
                x, y = weak[min_index]

                if win32api.GetKeyState(0x02) in (-127, -128) \
                        and not (half - 1 <= x + half <= half + 1 and half - 1 <= y + half <= half + 1):
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x * scale_weak), int(y * scale_weak), 0, 0)

                if win32api.GetKeyState(0x02) in (-127, -128) \
                        and half - hitweak <= x + half <= half + hitweak \
                        and half - hitweak <= y + half <= half + hitweak \
                        and checkbox2.get() == 1:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                cv2.line(frame, (int(half), int(half)), (x + int(half), y + int(half)), (0, 0, 255), 1)
                cv2.circle(frame, (int(x + half), int(y + half)), 2, (0, 255, 0), -1)

        window(frame)

import time
import math
import customtkinter as ctk
import cv2
import mss
import numpy as np
import torch
import win32api
import win32con
from PIL import Image, ImageTk

game = 50
trigger = 16

width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) / 2
height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) / 2
start_time = time.time()
wconst = 400
frame_count = 0
fps = 0
scale = 1.25
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

model = torch.hub.load('ultralytics/yolov5', 'custom', path='apex.pt')
model.conf = 0.69


def window(window0):
    img0 = cv2.cvtColor(window0, cv2.COLOR_BGR2RGB)
    img0 = cv2.resize(img0, (640, 640), interpolation=cv2.INTER_AREA)
    img0 = ImageTk.PhotoImage(Image.fromarray(img0))
    img.configure(image=img0)
    label.configure(text=f"FPS: {round(fps)}")


while True:
    root.update()
    # noinspection PyTypeChecker
    frame = np.array(screen.grab(detection_box))
    window(frame)
    start_time = time.time()
    frame_count = 0
    fps = 0

    while checkbox1.get() == 1:
        root.update()
        frame_count += 1
        elapsed_time = time.time() - start_time
        if elapsed_time != 0:
            fps = frame_count / elapsed_time
        # noinspection PyTypeChecker
        frame = np.array(screen.grab(detection_box))
        results = model(frame)

        if len(results.xyxy[0]) != 0:
            distances = []
            targets = []
            distances.clear()
            targets.clear()
            for box in results.xyxy[0]:
                x2 = int(box[2])
                x1 = int(box[0])
                y2 = int(box[3])
                y1 = int(box[1])
                x = int(((x1 + x2) / 2) - half)
                y = int(((y1 + y2) / 2) - ((y2 - y1) / game) - half)
                dist = math.sqrt(x * x + y * y)
                distances.append(dist)
                targets.append((x, y))
                cv2.circle(frame, (int(x + half), int(y + half)), 2, (0, 255, 0), -1)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)

            if len(distances) != 0:
                min_index = distances.index(min(distances))
                x, y = targets[min_index]

                if win32api.GetKeyState(0x02) in (-127, -128) \
                        and not (half - 1 <= x + half <= half + 1 and half - 1 <= y + half <= half + 1):
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x * scale), int(y * scale), 0, 0)

                if win32api.GetKeyState(0x02) in (-127, -128) \
                        and half - trigger <= x + half <= half + trigger \
                        and half - trigger <= y + half <= half + trigger \
                        and checkbox2.get() == 1:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                cv2.line(frame, (int(half), int(half)), (x + int(half), y + int(half)), (0, 0, 255), 1)
        window(frame)

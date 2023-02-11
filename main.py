import mss
import numpy as np
import torch
import win32api
import win32con
import cv2
import ctypes
import customtkinter as ctk
from PIL import Image, ImageTk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
root = ctk.CTk()
root.geometry("640x640")
root.title("Options")
frame = ctk.CTkFrame(master=root)

width = ctypes.windll.user32.GetSystemMetrics(0) / 2
height = ctypes.windll.user32.GetSystemMetrics(1) / 2
window_constant = 250
scale = 2

screen = mss.mss()
detection_box = {'left': int(width - (window_constant / 2)), 'top': int(height - (window_constant / 2)),
                 'width': int(window_constant), 'height': int(window_constant)}
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')
model.conf = 0.75

checkbox1 = ctk.CTkCheckBox(master=root, text="Softaim")
checkbox1.pack(ipadx=310, pady=10)

checkbox2 = ctk.CTkCheckBox(master=root, text="Triggerbot")
checkbox2.pack(ipadx=310)

img0 = None
img = ctk.CTkLabel(root, image=img0, text="")
img.pack()

while True:
    root.update()
    while checkbox1.get() == 1:
        root.update()

        if cv2.waitKey(250) & 0xFF == ord('0'):
            break

        frame = np.array(screen.grab(detection_box))
        results = model(frame)

        if len(results.xyxy[0]) != 0:
            for box in results.xyxy[0]:
                x2 = int(box[2])
                x1 = int(box[0])
                y2 = int(box[3])
                y1 = int(box[1])
                x = int(((x1 + x2) / 2) - (window_constant / 2))
                y = int(((y1 + y2) / 2) - ((y2 - y1) / 2.2) - (window_constant / 2))

                if win32api.GetKeyState(0x02) in (-127, -128) and not ((window_constant / 2) - 1 <= x + window_constant / 2 <= (window_constant / 2) + 1 and (window_constant / 2) - 1 <= y + window_constant / 2 <= (window_constant / 2) + 1):
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x * scale), int(y * scale), 0, 0)

                if win32api.GetKeyState(0x02) in (-127, -128) and (window_constant / 2) - 6 <= x + window_constant / 2 <= (window_constant / 2) + 6 and (
                        window_constant / 2) - 6 <= y + window_constant / 2 <= (
                        window_constant / 2) + 6 and checkbox2.get() == 1:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

            cv2.circle(frame, (int(x + (window_constant / 2)), int(y + (window_constant / 2))), 2, (0, 255, 0), -1)
            cv2.line(frame, (int(window_constant / 2), int(window_constant / 2)),
                     (x + int(window_constant / 2), y + int(window_constant / 2)), (0, 0, 255), 1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)
        img0 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img0 = cv2.resize(img0, (440, 440), interpolation=cv2.INTER_AREA)
        img0 = ImageTk.PhotoImage(Image.fromarray(img0))
        img.configure(image=img0)

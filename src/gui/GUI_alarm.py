import cv2
import tkinter as tk
from tkinter import messagebox, Toplevel, Listbox, Scrollbar
from PIL import Image, ImageTk
import numpy as np
import math
import time
import os
import threading
from datetime import datetime
from ai_edge_litert.interpreter import Interpreter

class MarineVisionFinal:
    def __init__(self, window):
        self.window = window
        self.window.title("SYSTEM WIZYJNY USV - PANEL OPERACYJNY")
        self.window.geometry("1100x850")
        self.window.configure(bg="#121212")

        # --- PARAMETRY SYMULACJI ---
        self.curr_speed = 45      
        self.curr_battery = 82    
        self.curr_temp = 36       
        self.curr_heading = 45    

        # --- LOGIKA SYSTEMOWA I WĄTKI ---
        self.video_writer = None
        self.is_recording = False
        self.is_running = True    
        self.last_detections = [] 
        self.logged_alarms = [] # Bufor, aby nie dublować wpisów w jednej sesji
        self.log_file = "historia_alarmow.txt"

        # --- KONFIGURACJA AI ---
        self.model_path = "mobilenet_v2_cpu.tflite"
        self.class_labels = {0: 'CZLOWIEK', 8: 'LODKA'}
        self.setup_ai()

        # --- BUDOWA GUI ---
        self.setup_ui()
        
        self.vid = cv2.VideoCapture(0)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.ai_thread = threading.Thread(target=self.ai_loop, daemon=True)
        self.ai_thread.start()
        
        self.update_gui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def setup_ai(self):
        if os.path.exists(self.model_path):
            try:
                self.interpreter = Interpreter(model_path=self.model_path, num_threads=4)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()[0]
                self.output_details = self.interpreter.get_output_details()
                self.h, self.w = self.input_details['shape'][1], self.input_details['shape'][2]
                self.ai_active = True
            except Exception as e:
                self.ai_active = False

    def ai_loop(self):
        while self.is_running:
            if self.ai_active:
                ret, frame = self.vid.read()
                if ret:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    interp_input = cv2.resize(rgb, (self.w, self.h))
                    input_data = np.expand_dims(interp_input, axis=0)

                    self.interpreter.set_tensor(self.input_details['index'], input_data)
                    self.interpreter.invoke()
                    
                    boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
                    classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
                    scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]

                    detections = []
                    for i in range(len(scores)):
                        if scores[i] > 0.5:
                            name = self.class_labels.get(int(classes[i]), f"ID:{int(classes[i])}")
                            detections.append({
                                'box': boxes[i],
                                'class': name,
                                'score': scores[i]
                            })
                            # LOGOWANIE DO PLIKU (Zadanie PR_2)
                            self.log_alarm_to_file(name)
                    
                    self.last_detections = detections
            time.sleep(0.01)

    def log_alarm_to_file(self, object_name):
        """Zapisuje alarm do pliku TXT """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] WYKRYTO: {object_name}\n"
        
        # Sprawdzamy czy ten sam alarm nie był przed chwilą (co 5 sek max)
        if not self.logged_alarms or (time.time() - self.logged_alarms[-1]['t'] > 5):
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
            self.logged_alarms.append({'t': time.time()})
            print(f"Zalogowano do pliku: {object_name}")

    def show_history(self):
        """Otwiera nowe okno z historią alarmów"""
        history_win = Toplevel(self.window)
        history_win.title("HISTORIA WYKRYTYCH OBIEKTÓW")
        history_win.geometry("500x400")
        history_win.configure(bg="#1e1e1e")

        tk.Label(history_win, text="REJESTR ZDARZEŃ", fg="white", bg="#1e1e1e", font=("Arial", 12, "bold")).pack(pady=10)

        # Przewijana lista
        frame = tk.Frame(history_win)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = Listbox(frame, bg="#2d2d2d", fg="white", font=("Consolas", 10), yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Wczytywanie z pliku
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines): # Najnowsze na górze
                    listbox.insert(tk.END, line.strip())
        else:
            listbox.insert(tk.END, "Brak zapisanych alarmów.")

    def setup_ui(self):
        self.top_frame = tk.Frame(self.window, bg="#1e1e1e", height=140, bd=1, relief=tk.SOLID)
        self.top_frame.pack(fill=tk.X, side=tk.TOP)

        self.tele_canvas = tk.Canvas(self.top_frame, width=600, height=130, bg="#1e1e1e", highlightthickness=0)
        self.tele_canvas.pack(side=tk.LEFT, padx=10)

        self.alarm_msg = tk.Label(self.top_frame, text="STATUS: SYSTEM OK", fg="#00ff00", bg="#1e1e1e", font=("Arial", 16, "bold"), wraplength=350)
        self.alarm_msg.pack(side=tk.LEFT, expand=True)

        self.time_label = tk.Label(self.top_frame, text="", fg="white", bg="#1e1e1e", font=("Consolas", 12), justify=tk.RIGHT)
        self.time_label.pack(side=tk.RIGHT, padx=20)

        self.cam_canvas = tk.Canvas(self.window, bg="black", highlightthickness=0)
        self.cam_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.bottom_frame = tk.Frame(self.window, bg="#121212", height=80)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        for i in range(3): self.bottom_frame.columnconfigure(i, weight=1)

        btn_font = ("Arial", 11, "bold")
        # --- TUTAJ DODANO COMMAND ---
        tk.Button(self.bottom_frame, text="HISTORIA ALARMÓW", bg="#c0392b", fg="white", font=btn_font, pady=15, 
                  command=self.show_history).grid(row=0, column=0, sticky="nsew", padx=2, pady=5)
        
        self.btn_video = tk.Button(self.bottom_frame, text="ZAPIS WIDEO", bg="#2980b9", fg="white", font=btn_font, pady=15, 
                                   command=self.toggle_record)
        self.btn_video.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)
        
        tk.Button(self.bottom_frame, text="ZAPIS ZDJĘCIA", bg="#27ae60", fg="white", font=btn_font, pady=15, 
                  command=self.take_photo).grid(row=0, column=2, sticky="nsew", padx=2, pady=5)

    def draw_telemetry(self):
        self.tele_canvas.delete("all")
        cx, cy, r = 75, 70, 55
        self.tele_canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=-30, extent=240, outline="white", style=tk.ARC, width=3)
        angle = -30 + (min(self.curr_speed, 100) / 100) * 240
        rad = math.radians(180 - angle)
        self.tele_canvas.create_line(cx, cy, cx + r*math.cos(rad), cy - r*math.sin(rad), fill="red", width=4)
        self.tele_canvas.create_text(cx, cy+30, text=f"{self.curr_speed} m/s", fill="white", font=("Arial", 16, "bold"))
        bx, by, bw, bh = 180, 30, 40, 80
        self.tele_canvas.create_rectangle(bx, by, bx+bw, by+bh, outline="white", width=2)
        fill_h = (self.curr_battery / 100) * (bh - 4)
        self.tele_canvas.create_rectangle(bx+2, by+bh-2-fill_h, bx+bw-2, by+bh-2, fill="#00ff00", outline="")
        self.tele_canvas.create_text(bx+bw+55, by+bh/2, text=f"{self.curr_battery}%", fill="white", font=("Arial", 22, "bold"))
        tx, ty = 350, 70
        self.tele_canvas.create_line(tx, ty-30, tx, ty+10, fill="white", width=5)
        self.tele_canvas.create_oval(tx-9, ty+5, tx+9, ty+23, fill="red", outline="white")
        self.tele_canvas.create_text(tx+45, ty, text=f"{self.curr_temp}°C", fill="white", font=("Arial", 14, "bold"))
        kx, ky, kr = 510, 70, 50
        self.tele_canvas.create_oval(kx-kr, ky-kr, kx+kr, ky+kr, outline="#444", width=2)
        rad_k = math.radians(self.curr_heading - 90)
        self.tele_canvas.create_line(kx, ky, kx + kr*math.cos(rad_k), ky + kr*math.sin(rad_k), fill="#f1c40f", width=4, arrow=tk.LAST)
        self.tele_canvas.create_text(kx, ky-kr-12, text="N", fill="red", font=("Arial", 10, "bold"))

    def toggle_record(self):
        if not self.is_recording:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.video_writer = cv2.VideoWriter(f"rejs_{ts}.avi", fourcc, 20.0, (640, 480))
            self.is_recording = True
            self.btn_video.config(bg="red", text="STOP NAGRYWANIA")
        else:
            self.is_recording = False
            if self.video_writer: self.video_writer.release()
            self.btn_video.config(bg="#2980b9", text="ZAPIS WIDEO")

    def take_photo(self):
        ret, frame = self.vid.read()
        if ret:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"foto_{ts}.jpg", frame)

    def update_gui(self):
        ret, frame = self.vid.read()
        if ret:
            if self.is_recording and self.video_writer: self.video_writer.write(frame)
            detected_names = []
            for det in self.last_detections:
                ymin, xmin, ymax, xmax = det['box']
                l, t = int(xmin * frame.shape[1]), int(ymin * frame.shape[0])
                r, b = int(xmax * frame.shape[1]), int(ymax * frame.shape[0])
                cv2.rectangle(frame, (l, t), (r, b), (0, 0, 255), 2)
                cv2.putText(frame, det['class'], (l, t-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                detected_names.append(det['class'])

            if detected_names:
                obj_str = ", ".join(list(set(detected_names)))
                self.alarm_msg.config(text=f"WYKRYTO: {obj_str}", fg="red")
            else:
                self.alarm_msg.config(text="STATUS: SYSTEM OK", fg="#00ff00")

            self.draw_telemetry()
            self.time_label.config(text=datetime.now().strftime("%d.%m.%Y\n%H:%M:%S"))
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            cw, ch = self.cam_canvas.winfo_width(), self.cam_canvas.winfo_height()
            if cw > 10: img = img.resize((cw, ch))
            self.tk_img = ImageTk.PhotoImage(image=img)
            self.cam_canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)
        self.window.after(10, self.update_gui)

    def on_closing(self):
        self.is_running = False
        self.vid.release()
        self.window.destroy()

if __name__ == "__main__":
    MarineVisionFinal(tk.Tk())
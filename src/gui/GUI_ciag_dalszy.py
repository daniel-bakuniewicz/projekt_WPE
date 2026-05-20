import cv2
import tkinter as tk
from tkinter import messagebox
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
        self.curr_speed = 45      # m/s
        self.curr_battery = 82    # %
        self.curr_temp = 36       # °C
        self.curr_heading = 45    # stopnie (NE)

        # --- LOGIKA SYSTEMOWA I WĄTKI ---
        self.video_writer = None
        self.is_recording = False
        self.is_running = True    # Flaga działania aplikacji
        self.last_detections = [] # Bufor dla wątku AI

        # --- KONFIGURACJA AI (Zadanie ZR_A) ---
        self.model_path = "mobilenet_v2_cpu.tflite"
        self.class_labels = {
            0: 'CZLOWIEK', 1: 'ROWER', 2: 'SAMOCHOD', 3: 'MOTOCYKL', 
            8: 'LODKA', 14: 'PTAK', 15: 'KOT', 16: 'PIES'
        }
        self.setup_ai()

        # --- BUDOWA GUI ---
        self.setup_ui()
        
        # Inicjalizacja kamery (640x480 dla optymalizacji)
        self.vid = cv2.VideoCapture(0)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # URUCHOMIENIE WĄTKU DETEKCJI W TLE
        self.ai_thread = threading.Thread(target=self.ai_loop, daemon=True)
        self.ai_thread.start()
        
        self.update_gui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def setup_ai(self):
        """Inicjalizacja interpretera AI 

[Image of neural network architecture]
"""
        if os.path.exists(self.model_path):
            try:
                # num_threads=4 przyspiesza proces na RPi 5 i laptopach
                self.interpreter = Interpreter(model_path=self.model_path, num_threads=16)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()[0]
                self.output_details = self.interpreter.get_output_details()
                self.h, self.w = self.input_details['shape'][1], self.input_details['shape'][2]
                self.ai_active = True
                print(f"Model {self.model_path} załadowany. Rozmiar wejścia: {self.w}x{self.h}")
            except Exception as e:
                print(f"Błąd AI: {e}")
                self.ai_active = False
        else:
            print("Błąd: Nie znaleziono pliku modelu!")
            self.ai_active = False

    def ai_loop(self):
        """Pętla detekcji działająca niezależnie od GUI (Wątek 2)"""
        while self.is_running:
            if self.ai_active:
                ret, frame = self.vid.read()
                if ret:
                    # Przygotowanie obrazu
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    interp_input = cv2.resize(rgb, (self.w, self.h))
                    input_data = np.expand_dims(interp_input, axis=0)

                    # Inferencja
                    start_t = time.time()
                    self.interpreter.set_tensor(self.input_details['index'], input_data)
                    self.interpreter.invoke()
                    
                    # Pobranie wyników
                    boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
                    classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
                    scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]

                    # Przetwarzanie wyników do bufora
                    detections = []
                    for i in range(len(scores)):
                        if scores[i] > 0.5:
                            detections.append({
                                'box': boxes[i],
                                'class': self.class_labels.get(int(classes[i]), f"ID:{int(classes[i])}"),
                                'score': scores[i]
                            })
                    
                    self.last_detections = detections
                    print(f"AI Latency: {(time.time() - start_t)*1000:.1f}ms")
            
            time.sleep(0.01) # Oszczędność CPU

    def setup_ui(self):
        """Konstrukcja interfejsu (Zadanie PR_2)"""
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
        tk.Button(self.bottom_frame, text="HISTORIA ALARMÓW", bg="#c0392b", fg="white", font=btn_font, pady=15).grid(row=0, column=0, sticky="nsew", padx=2, pady=5)
        self.btn_video = tk.Button(self.bottom_frame, text="ZAPIS WIDEO", bg="#2980b9", fg="white", font=btn_font, pady=15, command=self.toggle_record)
        self.btn_video.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)
        tk.Button(self.bottom_frame, text="ZAPIS ZDJĘCIA", bg="#27ae60", fg="white", font=btn_font, pady=15, command=self.take_photo).grid(row=0, column=2, sticky="nsew", padx=2, pady=5)

    def draw_telemetry(self):
        """Rysowanie dynamicznych wskaźników"""
        self.tele_canvas.delete("all")
        cx, cy, r = 75, 70, 55
        self.tele_canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=-30, extent=240, outline="white", style=tk.ARC, width=3)
        angle = -30 + (min(self.curr_speed, 100) / 100) * 240
        rad = math.radians(180 - angle)
        self.tele_canvas.create_line(cx, cy, cx + r*math.cos(rad), cy - r*math.sin(rad), fill="red", width=4)
        self.tele_canvas.create_text(cx, cy+30, text=f"{self.curr_speed} m/s", fill="white", font=("Arial", 16, "bold"))

        bx, by, bw, bh = 180, 30, 40, 80
        self.tele_canvas.create_rectangle(bx, by, bx+bw, by+bh, outline="white", width=2)
        self.tele_canvas.create_rectangle(bx+12, by-7, bx+bw-12, by, fill="white") 
        fill_h = (self.curr_battery / 100) * (bh - 4)
        b_color = "#00ff00" if self.curr_battery > 20 else "#ff0000"
        self.tele_canvas.create_rectangle(bx+2, by+bh-2-fill_h, bx+bw-2, by+bh-2, fill=b_color, outline="")
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
            filename = f"rejs_{ts}.avi"
            w, h = int(self.vid.get(3)), int(self.vid.get(4))
            self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (w, h))
            self.is_recording = True
            self.btn_video.config(bg="red", text="STOP NAGRYWANIA")
        else:
            self.is_recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            self.btn_video.config(bg="#2980b9", text="ZAPIS WIDEO")

    def take_photo(self):
        ret, frame = self.vid.read()
        if ret:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"foto_{ts}.jpg", frame)

    def update_gui(self):
        """Pętla odświeżania GUI (Wątek 1 - PŁYNNY)"""
        ret, frame = self.vid.read()
        if ret:
            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)

            # Rysowanie detekcji z bufora AI
            detected_names = []
            for det in self.last_detections:
                ymin, xmin, ymax, xmax = det['box']
                l, t = int(xmin * frame.shape[1]), int(ymin * frame.shape[0])
                r, b = int(xmax * frame.shape[1]), int(ymax * frame.shape[0])
                cv2.rectangle(frame, (l, t), (r, b), (0, 0, 255), 2)
                cv2.putText(frame, det['class'], (l, t-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                detected_names.append(det['class'])

            # Aktualizacja statusu alarmów
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
        if self.video_writer: self.video_writer.release()
        self.vid.release()
        self.window.destroy()

if __name__ == "__main__":
    MarineVisionFinal(tk.Tk())
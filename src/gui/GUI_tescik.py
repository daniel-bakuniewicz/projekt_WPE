import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import math
import time
import os
from datetime import datetime
from ai_edge_litert.interpreter import Interpreter

class MarineVisionFinal:
    def __init__(self, window):
        self.window = window
        self.window.title("SYSTEM WIZYJNY USV - PANEL OPERACYJNY")
        self.window.geometry("1100x850")
        self.window.configure(bg="#121212")

        # --- PARAMETRY SYMULACJI (Zastąp odczytami z czujników) ---
        self.curr_speed = 45      # m/s
        self.curr_battery = 82    # %
        self.curr_temp = 36       # °C
        self.curr_heading = 45    # stopnie (NE)

        # --- LOGIKA ZAPISU WIDEO ---
        self.video_writer = None
        self.is_recording = False

        # --- KONFIGURACJA AI (Zadanie ZR_A) ---
        # Upewnij się, że ten plik jest w folderze!
        self.model_path = "mobilenet_v2_cpu.tflite"
        
        # DEFINICJA ETYKIET COCO (Dla standardowego modelu MobileNet SSD v2)
        # Poniżej najpopularniejsze klasy, w pełnej wersji jest ich 90.
        self.class_labels = {
            0: 'CZLOWIEK', 1: 'ROWER', 2: 'SAMOCHOD', 3: 'MOTOCYKL', 4: 'SAMOLOT',
            5: 'AUTOBUS', 6: 'POCIAG', 7: 'CIEZAROWKA', 8: 'LODKA', 9: 'SWIATLA',
            12: 'ZNAK STOP', 14: 'PTAK', 15: 'KOT', 16: 'PIES', 17: 'KON',
            # Dodaj więcej jeśli potrzebujesz, 8 to Lodka/Statek
        }

        self.setup_ai()

        # --- BUDOWA GUI ---
        self.setup_ui()
        
        # Inicjalizacja kamery
        self.vid = cv2.VideoCapture(0)
        
        self.update()
        self.window.mainloop()

    def setup_ai(self):
        """Ładowanie modelu detekcji na procesor (CPU)"""
        if os.path.exists(self.model_path):
            try:
                self.interpreter = Interpreter(model_path=self.model_path)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()[0]
                self.output_details = self.interpreter.get_output_details()
                self.h, self.w = self.input_details['shape'][1], self.input_details['shape'][2]
                self.ai_active = True
                print(f"Model {self.model_path} załadowany pomyślnie na CPU.")
            except Exception as e:
                print(f"Błąd inicjalizacji AI: {e}")
                self.ai_active = False
        else:
            print("Błąd: Nie znaleziono pliku modelu TFLite!")
            self.ai_active = False

    def setup_ui(self):
        """Konstrukcja interfejsu zgodnie ze schematem"""
        # 1. GÓRNY PANEL (Telemetria i Alarmy)
        self.top_frame = tk.Frame(self.window, bg="#1e1e1e", height=140, bd=1, relief=tk.SOLID)
        self.top_frame.pack(fill=tk.X, side=tk.TOP)

        self.tele_canvas = tk.Canvas(self.top_frame, width=600, height=130, bg="#1e1e1e", highlightthickness=0)
        self.tele_canvas.pack(side=tk.LEFT, padx=10)

        self.alarm_msg = tk.Label(self.top_frame, text="STATUS: SYSTEM OK", fg="#00ff00", bg="#1e1e1e", font=("Arial", 16, "bold"), wraplength=300)
        self.alarm_msg.pack(side=tk.LEFT, expand=True)

        self.time_label = tk.Label(self.top_frame, text="", fg="white", bg="#1e1e1e", font=("Consolas", 12), justify=tk.RIGHT)
        self.time_label.pack(side=tk.RIGHT, padx=20)

        # 2. ŚRODEK (Podgląd Kamery)
        self.cam_canvas = tk.Canvas(self.window, bg="black", highlightthickness=0)
        self.cam_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 3. DOLNY PANEL (Przyciski 1/3 szerokości)
        self.bottom_frame = tk.Frame(self.window, bg="#121212", height=80)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=1)
        self.bottom_frame.columnconfigure(2, weight=1)

        btn_font = ("Arial", 11, "bold")
        
        tk.Button(self.bottom_frame, text="HISTORIA ALARMÓW", bg="#c0392b", fg="white", font=btn_font, pady=15).grid(row=0, column=0, sticky="nsew", padx=2, pady=5)
        self.btn_video = tk.Button(self.bottom_frame, text="ZAPIS WIDEO", bg="#2980b9", fg="white", font=btn_font, pady=15, command=self.toggle_record)
        self.btn_video.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)
        tk.Button(self.bottom_frame, text="ZAPIS ZDJĘCIA", bg="#27ae60", fg="white", font=btn_font, pady=15, command=self.take_photo).grid(row=0, column=2, sticky="nsew", padx=2, pady=5)

    def draw_telemetry(self):
        """Dynamiczne rysowanie wskaźników"""
        self.tele_canvas.delete("all")
        
        # --- PRĘDKOŚCIOMIERZ ---
        cx, cy, r = 75, 70, 55
        self.tele_canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=-30, extent=240, outline="white", style=tk.ARC, width=3)
        angle = -30 + (min(self.curr_speed, 100) / 100) * 240
        rad = math.radians(180 - angle)
        self.tele_canvas.create_line(cx, cy, cx + r*math.cos(rad), cy - r*math.sin(rad), fill="red", width=4)
        self.tele_canvas.create_text(cx, cy+30, text=f"{self.curr_speed} m/s", fill="white", font=("Arial", 16, "bold"))

        # --- BATERIA ---
        bx, by, bw, bh = 180, 30, 40, 80
        self.tele_canvas.create_rectangle(bx, by, bx+bw, by+bh, outline="white", width=2)
        self.tele_canvas.create_rectangle(bx+12, by-7, bx+bw-12, by, fill="white") 
        fill_h = (self.curr_battery / 100) * (bh - 4)
        b_color = "#00ff00" if self.curr_battery > 20 else "#ff0000"
        self.tele_canvas.create_rectangle(bx+2, by+bh-2-fill_h, bx+bw-2, by+bh-2, fill=b_color, outline="")
        self.tele_canvas.create_text(bx+bw+55, by+bh/2, text=f"{self.curr_battery}%", fill="white", font=("Arial", 22, "bold"))

        # --- TERMOMETR ---
        tx, ty = 350, 70
        self.tele_canvas.create_line(tx, ty-30, tx, ty+10, fill="white", width=5)
        self.tele_canvas.create_oval(tx-9, ty+5, tx+9, ty+23, fill="red", outline="white")
        self.tele_canvas.create_text(tx+45, ty, text=f"{self.curr_temp}°C", fill="white", font=("Arial", 14, "bold"))

        # --- KOMPAS ---
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
            w = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
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

    def update(self):
        """Pętla czasu rzeczywistego z aktywną detekcją i nazwami obiektów"""
        ret, frame = self.vid.read()
        if ret:
            # 1. Nagrywanie
            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)

            # 2. DETEKCJA AI (Zadanie ZR_A + Nowe nazwy obiektów)
            detected_objects = [] # Lista do przechowywania nazw wykrytych obiektów w tej klatce
            
            if self.ai_active:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                interp_input = cv2.resize(rgb, (self.w, self.h))
                input_data = np.expand_dims(interp_input, axis=0)

                self.interpreter.set_tensor(self.input_details['index'], input_data)
                self.interpreter.invoke()

                # Pobranie wyników
                boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
                classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0] # ID klas
                scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]

                for i in range(len(scores)):
                    if scores[i] > 0.5:
                        # Pobranie nazwy obiektu z mapy na podstawie ID klasy
                        class_id = int(classes[i])
                        class_name = self.class_labels.get(class_id, f"Obiekt {class_id}")
                        detected_objects.append(class_name) # Dodanie do listy alarmu

                        ymin, xmin, ymax, xmax = boxes[i]
                        left = int(xmin * frame.shape[1])
                        top = int(ymin * frame.shape[0])
                        right = int(xmax * frame.shape[1])
                        bottom = int(ymax * frame.shape[0])
                        
                        # Rysowanie czerwonej ramki
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                        
                        # RYSOWANIE NAZWY OBIEKTU NAD RAMKĄ
                        label_text = f"{class_name} ({int(scores[i]*100)}%)"
                        # Tło pod napis dla czytelności
                        (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                        cv2.rectangle(frame, (left, top - text_h - 5), (left + text_w, top), (0,0,255), -1)
                        # Napis biały na czerwonym tle
                        cv2.putText(frame, label_text, (left, top - 5), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # 3. AKTUALIZACJA GUI I KONSOLI
            self.draw_telemetry()
            ts_now = datetime.now().strftime("%d.%m.%Y\n%H:%M:%S")
            self.time_label.config(text=ts_now)
            
            # Unikalna lista wykrytych obiektów (żeby nie pisać 3 razy "CZLOWIEK")
            unique_detections = sorted(list(set(detected_objects)))

            if unique_detections:
                txt_alarm = "WYKRYTO: " + ", ".join(unique_detections)
                # Ograniczenie długości tekstu w GUI
                if len(txt_alarm) > 35: txt_alarm = txt_alarm[:32] + "..."
                self.alarm_msg.config(text=f"!!! {txt_alarm} !!!", fg="red")
                
                # PRINTOWANIE DO KONSOLI
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {', '.join(unique_detections)}")
            else:
                self.alarm_msg.config(text="STATUS: SYSTEM OK", fg="#00ff00")

            # Wyświetlanie obrazu
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            cw, ch = self.cam_canvas.winfo_width(), self.cam_canvas.winfo_height()
            if cw > 10: img = img.resize((cw, ch))
            self.tk_img = ImageTk.PhotoImage(image=img)
            self.cam_canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)

        self.window.after(120, self.update)

if __name__ == "__main__":
    MarineVisionFinal(tk.Tk())
DOKUMENTACJA SYSTEMU WIZYJNEGO DO WYKRYWANIA OBIEKTÓW NA MORZU

OPIS OGÓLNY
System ten to rozwiązanie wizyjne oparte na algorytmach sztucznej inteligencji, przeznaczone dla autonomicznych jednostek pływających. Głównym celem systemu jest automatyczne wykrywanie obiektów na otwartym akwenie (takich jak inne statki lub ludzie w wodzie) w celu zwiększenia bezpieczeństwa nawigacji i uniknięcia kolizji.

SEGMENTY SYSTEMU

SYSTEM WIZYJNY (GŁÓWNY PANEL)
Przedstawia widok w czasie rzeczywistym z kamery zamontowanej na dziobie jednostki. W momencie wykrycia obiektu przez model AI, system automatycznie nakłada na obraz ramkę (prostokąt) oznaczającą lokalizację przeszkody oraz etykietę z nazwą wykrytego obiektu.

PASEK GÓRNY (TELEMETRIA I ALARMY OBECNIE W FORMIE STATYCZNEJ NA CEL PREZENTACJI ZAMYSŁU)
Dostarcza kluczowych danych o stanie jednostki i otoczeniu:
-- Prędkość: Aktualna prędkość jednostki wyrażona w m/s, prezentowana na wskaźniku łukowym.
-- Bateria: Graficzna ikona poziomu naładowania z procentowym wskaźnikiem stanu energii.
-- Temperatura: Odczyt temperatury otoczenia prezentowany obok ikony termometru.
-- Kompas: Dynamiczna tarcza wskazująca aktualny kierunek płynięcia.
-- Alarmy: Pole tekstowe wyświetlające nazwę wykrytego obiektu (np. LODKA) w momencie wystąpienia zagrożenia.
-- Czas: Bieżąca data oraz godzina systemowa.

PASEK DOLNY (OBSŁUGA I REJESTRACJA)
Zawiera przyciski sterujące rozciągnięte na pełną szerokość okna (podział 1/3):
-- Historia alarmów: Przycisk otwierający rejestr wszystkich dotychczas wykrytych obiektów.
-- Zapis wideo: Umożliwia nagrywanie obrazu z kamery do pliku. Przycisk zmienia tryb na STOP podczas trwania nagrania.
-- Zapis zdjęcia: Wykonuje natychmiastowy zrzut ekranu z podglądu kamery i zapisuje go w formacie JPG.

WYMAGANIA TECHNICZNE

Komputer sterujący: Mikrokomputer jednoukładowy Raspberry Pi 5 8GB: 

Kamera : Raspberry Pi Camera HD v2 8MPx

Uchwyt do kamery Raspberry Pi

Ekran wizyjny: Raspberry Pi Monitor - ekran LCD IPS 15,6'' 1920x1080px HDMI + USB

Model AI: MobileNet SSD V2 (zoptymalizowany pod procesory CPU).


Program został stworzony z wykorzystaniem środowiska programistycznego Python wraz z niezbędnymi bibliotekami.
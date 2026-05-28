# Projekt z przedmiotu Wodne Pojazdy Elektryczne - Zespół ZR_A

## 🎯 Cel Projektu
Celem naszego zespołu jest zaprojektowanie i wykonanie wbudowanego systemu wizyjnego, który wykorzystuje sztuczną inteligencję do **detekcji obiektów i zagrożeń** w środowisku wodnym. System ma na celu zwiększenie autonomii pojazdu poprzez rozpoznawanie m.in. kamieni, ludzi, znaków wodnych oraz kei.

## 💻 Wykorzystywany Sprzęt
* **Komputer:** Raspberry Pi 5 (8GB RAM) 
* **Akcelerator AI:** Google Coral USB Accelerator (Edge TPU) 
* **Kamera:** Raspberry Pi Camera HD v2 8MPx
* **Monitor:** Ekran LCD IPS 15,6"

---

## 👥 Podział Zespołu i Zadania

### 📂 Podzespół PR_1: Dane, Modele i Dokumentacja
**Skład osobowy:**
1. Daniel Bakuniewicz
2. Kacper Drulla

**Zakres obowiązków:**
* **Akwizycja danych:** Pozyskanie obrazów z kamery w różnych scenariuszach wodnych.
* **Przygotowanie zbioru danych:** Anotacja (etykietowanie) obiektów takich jak ludzie, przeszkody, znaki i keje.
* **Model AI:** Dobór, trenowanie oraz konwersja modelu do formatu zgodnego z Edge TPU (Google Coral).
* **Dokumentacja:** Przygotowanie opisu modeli, wymagań sprzętowych i instrukcji uruchomienia.

### 📂 Podzespół PR_2: Implementacja, Integracja i GUI
**Skład osobowy:**
1. Jan Kowalewski
2. Hubert Gołębiowski
3. Szymon Ciechański

**Zakres obowiązków:**
* **Kodowanie:** Implementacja skryptów Python do przetwarzania obrazu i inferencji na Edge TPU.
* **Integracja:** Połączenie oprogramowania z akceleratorem Google Coral w celu optymalizacji pracy w czasie rzeczywistym.
* **Interfejs GUI:** Stworzenie graficznego interfejsu użytkownika umożliwiającego podgląd z kamery i wizualizację detekcji (ramki/etykiety).
* **Testy:** Walidacja poprawności działania całego systemu.

---


# Dokumentacja techniczna podzespołu PR_1:

## 1. Cel podzespołu
Podzespół PR_1 odpowiada za zarządzanie danymi wejściowymi oraz optymalizację i uruchomienie modeli sztucznej inteligencji bezpośrednio na procesorze (CPU) platformy wbudowanej:
* **Akwizycja danych:** Pozyskiwanie obrazów i sekwencji wideo z kamery w rzeczywistym środowisku wodnym.
* **Przygotowanie zbioru danych:** Anotacja (etykietowanie) kluczowych obiektów i zagrożeń nawigacyjnych.
* **Model AI:** Dobór i dostosowanie modeli detekcyjnych do formatu TensorFlow Lite (`.tflite`) zoptymalizowanego pod kątem wydajnej inferencji na wielordzeniowym procesorze CPU.
* **Dokumentacja:** Przygotowanie opisów technicznych, wymagań systemowych oraz procedur uruchomieniowych.

## 2. Wymagania sprzętowe
Wszystkie obliczenia związane z detekcją obiektów w czasie rzeczywistym są wykonywane bezpośrednio przez jednostkę centralną mikrokomputera (inferencja na CPU).

| Komponent | Model | Parametry kluczowe |
| :--- | :--- | :--- |
| **Komputer SBC** | Raspberry Pi 5 (8GB RAM) | Główna jednostka obliczeniowa (ARM Cortex-A76 @ 2.4 GHz) |
| **Kamera** | Raspberry Pi Camera HD v2 | 8 Mpx, przetwornik Sony IMX219, interfejs CSI-2 |
| **System operacyjny** | Raspberry Pi OS (64-bit) | Wersja Trixie (Debian 13) |

## 3. Cykl życia danych

### 3.1 Akwizycja danych
Dane wejściowe w postaci plików graficznych oraz strumienia wideo są rejestrowane przy użyciu dedykowanej kamery na platformie USV podczas rejsów testowych. Baza danych budowana jest w oparciu o różnorodne scenariusze operacyjne, uwzględniając zmienne pory dnia, warunki oświetleniowe oraz czynniki atmosferyczne (pełne słońce, zachmurzenie, mgła, fale).

### 3.2 Klasy anotacji
Potok przetwarzania danych i model detekcji wspierają rozpoznawanie obiektów kluczowych z punktu widzenia autonomii i bezpieczeństwa jednostki pływającej. Wykorzystywane klasy obejmują m.in.:
* `person` (człowiek w wodzie / na pomoście)
* `boat` (obce jednostki pływające, łodzie)

## 4. Architektura modelu i środowisko obliczeniowe
Ze względu na realizację zadań detekcji wyłącznie na CPU, potok wykonawczy został oparty o niskonarzutowe i lekkie biblioteki interpretujące grafy obliczeniowe.

* **Format modelu:** Standardowy format TensorFlow Lite (`.tflite`) przeznaczony dla urządzeń wbudowanych (np. `mobilenet_v2_cpu.tflite`).
* **Alokacja zasobów:** Interpreter TFLite ładuje model bezpośrednio do pamięci operacyjnej RAM mikrokomputera, rozkładając operacje matematyczne (sploty, warstwy gęste) na dostępne rdzenie procesora ARM za pomocą optymalizacji wielowątkowej.
* **Przetwarzanie wstępne (Preprocessing):** Każda klatka przechwycona z kamery jest skalowana do rozdzielczości wejściowej modelu (np. `224x224` pikseli) oraz konwertowana z formatu BGR (natywnego dla OpenCV) do przestrzeni barwnej RGB oczekiwanej przez sieć neuronową.

## 5. Środowisko programistyczne i zależności
Lista pakietów została ograniczona wyłącznie do bibliotek niezbędnych do obsługi kamer oraz wykonywania modeli na architekturze procesora, co eliminuje narzut związany z zewnętrznymi sterownikami sprzętowymi.

### Kluczowe pakiety (`requirements.txt`):
* `opencv-python` – biblioteka odpowiedzialna za niskopoziomową obsługę kamery systemowej (`/dev/video0`), operacje na macierzach pikseli (zmiana rozmiaru, przestrzeni barw) oraz renderowanie nałożonych ramek detekcji (bounding boxes).
* `numpy` – pakiet wspierający szybkie operacje numeryczne i transformacje kształtu tensorów przed podaniem ich na wejście interpretera.

## 6. Procedura wdrożenia i uruchomienia

### 6.1 Konfiguracja środowiska wirtualnego
Instalację wszystkich zależności oraz uruchamianie skryptów należy przeprowadzać wewnątrz odizolowanego środowiska Python:

```bash
# Przejście do katalogu źródłowego projektu
cd src/

# Tworzenie środowiska wirtualnego
python -m venv venv

# Aktywacja środowiska wirtualnego (Linux / Raspberry Pi OS)
source venv/bin/activate

# Aktualizacja managera pakietów i instalacja zależności
pip install -r requirements.txt
```
### 6.2 Uruchomienie aplikacji detekcyjnej

Po prawidłowej konfiguracji środowiska, proces inferencji na CPU uruchamia się za pomocą skryptu głównego lub powiązanego interfejsu graficznego (GUI):

```bash
python3 main.py
```
### 6.3 Algorytm działania programu na CPU
1. Inicjalizacja: Program wywołuje klasę interpretera, ładując plik wag modelu .tflite oraz powiązany plik mapowania etykiet tekstowych.

2. Przechwytywanie obrazu: OpenCV otwiera strumień wideo z kamery i w pętli pobiera surowe klatki.
3. Przygotowanie wejścia: Klatka jest transformowana do formatu RGB i skalowana, a następnie przekazywana do odpowiedniego tensora wejściowego interpretera.
4. Wykonanie obliczeń (Inferencja): Wywołanie metody interpreter.invoke() zmusza procesor Raspberry Pi 5 do sekwencyjnego przeliczenia warstw sieci.
5. Przetwarzanie wyjścia (Postprocessing): Skrypt odczytuje z tensora wyjściowego znormalizowane współrzędne wykrytych obiektów, przypisuje im odpowiednie nazwy z pliku etykiet i rysuje na ekranie ramki wraz z poziomem pewności (score wyrażony w %).

# Dokumentacja techniczna podzespołu PR_2:



## 1. OPIS OGÓLNY
System wizyjny do wykrywania obiektów na morzu to rozwiązanie wizyjne oparte na algorytmach sztucznej inteligencji, przeznaczone dla autonomicznych jednostek pływających. Głównym celem systemu jest automatyczne wykrywanie obiektów na otwartym akwenie (takich jak inne statki lub ludzie w wodzie) w celu zwiększenia bezpieczeństwa nawigacji i uniknięcia kolizji.

## 2. SEGMENTY SYSTEMU

### 2.1 SYSTEM WIZYJNY (GŁÓWNY PANEL)
Przedstawia widok w czasie rzeczywistym z kamery zamontowanej na dziobie jednostki. W momencie wykrycia obiektu przez model AI, system automatycznie nakłada na obraz ramkę (prostokąt) oznaczającą lokalizację przeszkody oraz etykietę z nazwą wykrytego obiektu.

### 2.2 PASEK GÓRNY (TELEMETRIA I ALARMY OBECNIE W FORMIE STATYCZNEJ NA CEL PREZENTACJI ZAMYSŁU)
Dostarcza kluczowych danych o stanie jednostki i otoczeniu:
- Prędkość: Aktualna prędkość jednostki wyrażona w m/s, prezentowana na wskaźniku łukowym.
- Bateria: Graficzna ikona poziomu naładowania z procentowym wskaźnikiem stanu energii.
- Temperatura: Odczyt temperatury otoczenia prezentowany obok ikony termometru.
- Kompas: Dynamiczna tarcza wskazująca aktualny kierunek płynięcia.
- Alarmy: Pole tekstowe wyświetlające nazwę wykrytego obiektu (np. LODKA) w momencie wystąpienia zagrożenia.
- Czas: Bieżąca data oraz godzina systemowa.

### 2.3 PASEK DOLNY (OBSŁUGA I REJESTRACJA)
Zawiera przyciski sterujące rozciągnięte na pełną szerokość okna (podział 1/3):
- Historia alarmów: Przycisk otwierający rejestr wszystkich dotychczas wykrytych obiektów.
- Zapis wideo: Umożliwia nagrywanie obrazu z kamery do pliku. Przycisk zmienia tryb na STOP podczas trwania nagrania.
- Zapis zdjęcia: Wykonuje natychmiastowy zrzut ekranu z podglądu kamery i zapisuje go w formacie JPG.

## 3. WYMAGANIA TECHNICZNE

Komputer sterujący: Mikrokomputer jednoukładowy Raspberry Pi 5 8GB: 

Kamera : Raspberry Pi Camera HD v2 8MPx

Uchwyt do kamery Raspberry Pi

Ekran wizyjny: Raspberry Pi Monitor - ekran LCD IPS 15,6'' 1920x1080px HDMI + USB

Model AI: MobileNet SSD V2 (zoptymalizowany pod procesory CPU).


Program został stworzony z wykorzystaniem środowiska programistycznego Python wraz z niezbędnymi bibliotekami.

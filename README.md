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

## 🚀 Instrukcja Uruchomienia
(później)

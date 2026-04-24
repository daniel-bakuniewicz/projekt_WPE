# Podzespół PR_2: Implementacja, integracja i GUI (Zespół ZR_A)

## 👥 Skład zespołu
* **Jan Kowalewski**
* **Hubert Gołębiowski**
* **Szymon Ciechański**

## 🎯 Zakres odpowiedzialności
Podzespół PR_2 odpowiada za stworzenie warstwy programowej, która połączy model AI ze sprzętem oraz udostępni interfejs dla użytkownika.

### 📋 Lista zadań:
* **Skrypty Python:** Implementacja oprogramowania do przetwarzania obrazu i uruchamiania inferencji na Edge TPU.
* **Integracja:** Połączenie skryptów z akceleratorem Google Coral USB Accelerator.
* **Optymalizacja:** Zapewnienie płynnego działania systemu w czasie rzeczywistym.
* **Wizualizacja:** Implementacja nakładek na obraz (ramki i etykiety wykrytych obiektów).
* **Graficzny interfejs (GUI):** Opracowanie aplikacji umożliwiającej:
    * Podgląd obrazu z kamery na żywo.
    * Wyświetlanie informacji o wykrytych zagrożeniach.
    * Podstawową konfigurację systemu.
* **Testy:** Walidacja poprawności działania całego prototypu na Raspberry Pi 5.

## 🛠️ Technologie
* **Język:** Python
* **Biblioteki:** OpenCV, biblioteki graficzne GUI (np. Tkinter/PyQt)
* **Sprzęt:** Raspberry Pi 5, Monitor LCD IPS

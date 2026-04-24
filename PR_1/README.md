# Podzespół PR_1: Dane, modele i dokumentacja (Zespół ZR_A)

## 👥 Skład zespołu
* **Daniel Bakuniewicz**
* **Kacper Drulla**

## 🎯 Zakres odpowiedzialności
Głównym zadaniem podzespołu PR_1 jest przygotowanie „mózgu” systemu wizyjnego, czyli modelu sztucznej inteligencji zdolnego do rozpoznawania zagrożeń w środowisku wodnym.

### 📋 Lista zadań:
* **Akwizycja obrazu:** Pozyskanie materiału wizyjnego z kamery w różnych scenariuszach operacyjnych.
* **Zbiór danych:** Przygotowanie i anotacja (etykietowanie) zbioru danych obejmującego: ludzi, przeszkody, znaki wodne oraz keje.
* **Model AI:** Dobór odpowiedniej architektury oraz trenowanie modelu detekcji obiektów.
* **Konwersja:** Optymalizacja modelu do formatu zgodnego z akceleratorem Edge TPU (Google Coral).
* **Dokumentacja techniczna:** Opracowanie instrukcji uruchomienia, wymagań systemowych oraz opisu wykorzystanych modeli i danych.

## 🛠️ Technologie
* **Anotacja:** (np. CVAT / LabelImg)
* **Framework:** TensorFlow Lite / OpenCV 
* **Sprzęt:** Google Coral USB Accelerator 

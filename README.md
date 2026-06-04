# Wykorzystanie Dużych Modeli Językowych (LLM) do Automatycznego Generowania i Analizy Grafów Infrastruktury Liniowej z Użyciem Baz Grafowych

## Autorzy i Informacje o Projekcie
* **Autorzy:** Mateusz Młynek, Michał Szczepanik
* **Przedmiot:** Hurtownie Danych i Systemy Eksploracji Danych
* **Grupa:** Grupa nr 1 (USOS), BDiIS-1
* **Data:** 25.05.2026 r.
* **Projekt:** nr 25

---

## Cel i Opis Projektu
Projekt realizuje prototyp systemu automatycznej konwersji nieustrukturyzowanych, naturalnych tekstów technicznych (pochodzących z oficjalnych komunikatów **GDDKiA**) na strukturalną i połączoną bazę wiedzy w postaci **grafu**. 

System automatycznie wyodrębnia obiekty inżynieryjne, odcinki dróg, skrzyżowania oraz relacje przestrzenne i topologiczne między nimi, a następnie ładuje je do chmurowej bazy danych **Neo4j Aura** przy użyciu języka zapytań **Cypher**. Projekt rozwiązuje problem czasochłonnej i podatnej na błędy ręcznej digitalizacji infrastruktury liniowej.

---

## Architektura i Technologie
* **Język programowania:** Python 3.10+
* **Model LLM:** Google Gemini 2.5 Flash (`gemini-2.5-flash`) via `google-genai` SDK
* **Baza danych:** Neo4j Aura (Grafowa baza danych w chmurze)

---

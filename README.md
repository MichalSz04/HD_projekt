# Wykorzystanie Modelu Gemini i Bazy Neo4j do Analizy Grafów Infrastruktury Liniowej

Projekt realizuje automatyczną konwersję nieustrukturyzowanych tekstów technicznych (komunikaty GDDKiA) na model grafu właściwości w bazie danych Neo4j.

---

## Instrukcja Uruchomienia i Konfiguracja (Config)

### 1. Przygotowanie środowiska wirtualnego (Virtual Env)
W głównym katalogu projektu utwórz i aktywuj wirtualne środowisko Pythona, a następnie zainstaluj wymagane pakiety:

```bash
# Tworzenie środowiska wirtualnego
python -m venv .venv

# Aktywacja środowiska (Windows)
.venv\Scripts\activate

# Aktywacja środowiska (Linux/Mac)
source .venv/bin/activate

# Instalacja wymaganych bibliotek z pliku
pip install -r requirements.txt

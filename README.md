```markdown
#  Wykorzystanie Modelu Gemini i Bazy Neo4j do Analizy Grafów Infrastruktury Liniowej

Projekt realizuje automatyczną konwersję nieustrukturyzowanych tekstów technicznych (komunikaty GDDKiA) na model grafu właściwości (Labeled Property Graph) w bazie danych Neo4j.

---

##  Instrukcja Uruchomienia i Konfiguracja (Config)

### 1. Przygotowanie środowiska wirtualnego (Virtual Env)
W głównym katalogu projektu utwórz i aktywuj wirtualne środowisko Pythona, a następnie zainstaluj wymagane pakiety zewnętrzne zdefiniowane w pliku manifestu:

```bash
# Tworzenie środowiska wirtualnego
python -m venv .venv

# Aktywacja środowiska (System Windows)
.venv\Scripts\activate

# Aktywacja środowiska (Systemy Linux / macOS)
source .venv/bin/activate

# Instalacja wymaganych bibliotek z pliku requirements.txt
pip install -r requirements.txt

```

### 2. Konfiguracja zmiennych środowiskowych (.env)

Dane dostępowe do chmurowej bazy danych oraz klucze API zostały odizolowane od kodu źródłowego ze względów bezpieczeństwa.

1. Skopiuj plik demonstracyjny `.env.example` i utwórz na jego podstawie lokalny plik konfiguracyjny `.env`:
```bash
cp .env.example .env

```


2. Otwórz nowo utworzony plik `.env` i wprowadź swoje tajne klucze autoryzacyjne:
```env
NEO4J_URI=neo4j+s://twoj-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=twoje-haslo-do-bazy
GEMINI_API_KEY=twoj-klucz-api-gemini

```



### 3. Zasilenie danymi i uruchomienie programu

1. Upewnij się, że w katalogu głównym projektu znajduje się folder `data`. Jeśli katalog nie istnieje, program utworzy go automatycznie przy pierwszym uruchomieniu.
2. Umieść surowe pliki tekstowe (z rozszerzeniem `.txt`) zawierające opisy techniczne dróg w folderze `data`.
3. Uruchom główny skrypt aplikacji:
```bash
python nazwa_twojego_skryptu.py

```


4. Po wyświetleniu interaktywnego menu w konsoli, wpisz numery plików oddzielone spacją (np. `1 2 5`), aby rozpocząć ekstrakcję danych przez LLM i automatyczne zasilenie bazy Neo4j.

---

##  Wizualizacja i Przegląd Wyników w Neo4j Browser

Aby zweryfikować poprawność zaimportowanych danych i wyświetlić wygenerowany graf infrastruktury liniowej, zaloguj się do panelu **Neo4j Aura / Neo4j Browser** i użyj poniższych zapytań w języku **Cypher**:

### 1. Wyświetlenie całego wygenerowanego grafu

To podstawowe zapytanie, które pozwola zobaczyć pełną sieć powiązań (wszystkie pobrane węzły oraz relacje przestrzenne między nimi):

```cypher
MATCH (n) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m

```

### 2. Czyszczenie bazy danych (Reset przed kolejnym testem)

By usunąć wszystkie dane z bazy, aby przetestować kolejny graf należy przed wgraniem nowych danych do bazy wykonać zapytanie czyszczące:

```cypher
MATCH (n) DETACH DELETE n

```


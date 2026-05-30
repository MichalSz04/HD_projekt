import json
import os
from google import genai
from google.genai import types
from neo4j import GraphDatabase

# --- KONFIGURACJA ---
NEO4J_URI = ""
NEO4J_USER = ""
NEO4J_PASSWORD = ""
GEMINI_API_KEY = ""

# Inicjalizacja nowego klienta Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Jesteś ekspertem w dziedzinie inżynierii drogowej i analizy danych grafowych. Twoim zadaniem
jest przekształcanie tekstowych opisów infrastruktury liniowej na ustrukturyzowany format
JSON, który zostanie zaimportowany do bazy Neo4j.
1. DOPUSZCZALNE WĘZŁY I ATRYBUTY:
• Odcinek drogi: {nazwa, nawierzchnia, dlugosc, liczba_pasow, klasa}
• Skrzyżowanie: {nazwa, rodzaj, sygnalizacja (Tak/Nie)}
• Rondo: {nazwa, liczba_wlotow, lokalizacja}
• Obiekt inżynieryjny: {typ_obiektu (Most/Wiadukt/Tunel/Przepust), nazwa, nosnosc}
• Punkt POI: {kategoria, nazwa_wlasna}
2. DOPUSZCZALNE RELACJE:
• ŁĄCZY_SIĘ_Z: (Odcinek <-> Skrzyżowanie/Rondo)
• ZAWIERA: (Odcinek -> Obiekt inżynieryjny/Rondo)
• PRZECHODZI_NAD / PRZECHODZI_POD: (Obiekt inżynieryjny <-> Droga)
• DOJAZD_DO: (Odcinek/Obiekt -> Punkt POI)
3. ZASADY EKSTRAKCJI:
• Zwracaj wyniki WYŁĄCZNIE w formacie JSON.
• Każdy węzeł musi mieć unikalne ID (np. N1, N2).
• Jeśli brakuje jakiegoś atrybutu w tekście, pomiń go w obiekcie properties.
4. PRZYKŁADY (Few-Shot):
{
"document_info": {
"title": "Obwodnica Przecławia i Warzymic (DK13)",
"date": "2023-08-31",
"source_type": "Real-world technical description"
},
"nodes": [
{
"id": "N1",
"type": "Odcinek drogi",
"properties": {
"nazwa": "Obwodnica Przecławia i Warzymic - Etap I",
"dlugosc": 4.2,
"liczba_pasow": 4,
"klasa": "GP"
}
},
{
"id": "N2",
"type": "Odcinek drogi",
"properties": {
"nazwa": "Obwodnica Przecławia i Warzymic - Etap II",
"dlugosc": 2.3,
"klasa": "S/GP"
}
},
{
"id": "N3",
"type": "Odcinek drogi",
"properties": {
"nazwa": "Obwodnica Kołbaskowa",
"dlugosc": 5.6,
"liczba_pasow": 2,
"klasa": "GP"
}
},
{
"id": "N4",
"type": "Odcinek drogi",
"properties": {
"nazwa": "Autostrada A6"
}
},
{
"id": "N5",
"type": "Odcinek drogi",
"properties": {
"nazwa": "Droga lokalna Kurów - Przecław"
}
},
{
"id": "N6",
"type": "Rondo",
"properties": {
"nazwa": "Rondo Hakena",
"lokalizacja": "Szczecin"
}
},
{
"id": "N7",
"type": "Rondo",
"properties": {
"nazwa": "Rondo południowe",
"lokalizacja": "styk z DK13 na południe od Przecławia"
}
},
{
"id": "N8",
"type": "Rondo",
"properties": {
"nazwa": "Rondo Kołbaskowo-Moczyły"
}
},
{
"id": "N9",
"type": "Rondo",
"properties": {
"nazwa": "Rondo Rosówek"
}
},
{
"id": "N10",
"type": "Rondo",
"properties": {
"nazwa": "Rondo graniczne",
"lokalizacja": "Rosówek - Kamieniec"
}
},
{
"id": "N11",
"type": "Skrzyżowanie",
"properties": {
"nazwa": "Węzeł Przecław",
"rodzaj": "węzeł drogowy"
}
},
{
"id": "N12",
"type": "Skrzyżowanie",
"properties": {
"nazwa": "Węzeł Siadło Górne",
"rodzaj": "węzeł drogowy"
}
},
{
"id": "N13",
"type": "Skrzyżowanie",
"properties": {
"nazwa": "Węzeł Szczecin Zachód",
"rodzaj": "węzeł autostradowy"
}
},
{
"id": "N14",
"type": "Obiekt inżynieryjny",
"properties": {
"typ_obiektu": "Wiadukt",
"nazwa": "Wiadukt na węźle Przecław"
}
},
{
"id": "N15",
"type": "Obiekt inżynieryjny",
"properties": {
"typ_obiektu": "Wiadukt",
"nazwa": "Wiadukt w ciągu drogi Kurów - Przecław"
}
},
{
"id": "N16",
"type": "Obiekt inżynieryjny",
"properties": {
"typ_obiektu": "Przepust",
"nazwa": "Przepusty na obwodnicy"
}
}
],
"relationships": [
{ "source": "N6", "target": "N1", "type": "ŁĄCZY_SIĘ_Z" },
{ "source": "N1", "target": "N7", "type": "ŁĄCZY_SIĘ_Z" },
{ "source": "N1", "target": "N11", "type": "ZAWIERA" },
{ "source": "N1", "target": "N16", "type": "ZAWIERA" },
{ "source": "N14", "target": "N1", "type": "PRZECHODZI_NAD" },
{ "source": "N15", "target": "N1", "type": "PRZECHODZI_NAD" },
{ "source": "N12", "target": "N1", "type": "ŁĄCZY_SIĘ_Z" },
{ "source": "N2", "target": "N12", "type": "ŁĄCZY_SIĘ_Z" },
{ "source": "N2", "target": "N13", "type": "ŁĄCZY_SIĘ_Z" },
{ "source": "N13", "target": "N4", "type": "ŁĄCZY_SIĘ_Z" },
{ "source": "N3", "target": "N13", "type": "ŁĄCZY_SIĘ_Z" },
{ "source": "N3", "target": "N8", "type": "ZAWIERA" },
{ "source": "N3", "target": "N9", "type": "ZAWIERA" },
{ "source": "N3", "target": "N10", "type": "ZAWIERA" }
]
}
ZADANIE: Przeanalizuj poniższy tekst i wygeneruj graf JSON zgodnie z powyższym schematem:
"""


def extract_with_gemini(raw_text):
    print("Gemini analizuje tekst z parametrem (temperature=0.0)...")
    model_id = "gemini-2.5-flash"

    try:
        config = types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json"
        )

        response = client.models.generate_content(
            model=model_id,
            contents=f"{SYSTEM_PROMPT}\n\nTekst do analizy: {raw_text}",
            config=config
        )

        text_response = response.text
        clean_json = text_response.replace('```json', '').replace('```', '').strip()

        start_idx = clean_json.find('{')
        end_idx = clean_json.rfind('}') + 1
        final_json_str = clean_json[start_idx:end_idx]

        parsed_json = json.loads(final_json_str)

        print("\n" + "=" * 50)
        print("WYGENEROWANY STABILNY JSON:")
        print(json.dumps(parsed_json, indent=4, ensure_ascii=False))
        print("=" * 50 + "\n")

        with open("ostatni_wynik.json", "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, indent=4, ensure_ascii=False)
        print("Wynik zapisanego pliku: ostatni_wynik.json")

        return parsed_json

    except Exception as e:
        print(f"Błąd podczas komunikacji z modelem {model_id}: {e}")
        raise e


def save_to_neo4j(data):
    print("Rozpoczynam miękką walidację schematu i przesyłanie do Neo4j...")

    node_type_map = {node['id']: node['type'] for node in data.get('nodes', [])}

    VALID_ONTOLOGY = {
        "ŁĄCZY_SIĘ_Z": {
            ("Odcinek drogi", "Skrzyżowanie"), ("Skrzyżowanie", "Odcinek drogi"),
            ("Odcinek drogi", "Rondo"), ("Rondo", "Odcinek drogi")
        },
        "ZAWIERA": {
            ("Odcinek drogi", "Obiekt inżynieryjny"),
            ("Odcinek drogi", "Rondo")
        },
        "PRZECHODZI_NAD": {
            ("Obiekt inżynieryjny", "Odcinek drogi"),
            ("Odcinek drogi", "Obiekt inżynieryjny")
        },
        "PRZECHODZI_POD": {
            ("Obiekt inżynieryjny", "Odcinek drogi"),
            ("Odcinek drogi", "Obiekt inżynieryjny")
        },
        "DOJAZD_DO": {
            ("Odcinek drogi", "Punkt POI"),
            ("Obiekt inżynieryjny", "Punkt POI")
        }
    }

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:

        for node in data.get('nodes', []):
            query = f"MERGE (n:`{node['type']}` {{id: $id}}) SET n += $props"
            session.run(query, id=node['id'], props=node['properties'])

        for rel in data.get('relationships', []):
            source_id = rel['source']
            target_id = rel['target']
            rel_type = rel['type']

            is_valid = True
            reason = ""

            if source_id not in node_type_map or target_id not in node_type_map:
                is_valid = False
                reason = "Brak definicji jednego z węzłów w sekcji 'nodes'."
            else:
                source_type = node_type_map[source_id]
                target_type = node_type_map[target_id]

                if rel_type not in VALID_ONTOLOGY:
                    is_valid = False
                    reason = f"Nieznany typ relacji '{rel_type}' poza oficjalną specyfikacją."
                else:
                    current_pair = (source_type, target_type)
                    if current_pair not in VALID_ONTOLOGY[rel_type]:
                        is_valid = False
                        reason = f"Niedozwolone połączenie typów: ({source_type}) -[{rel_type}]-> ({target_type})."

            if not is_valid:
                print(f"WALIDACJA OSTRZEGAWCZA: Model utworzył relację niezgodną z ontologią!")
                print(f"   Połączenie: {source_id} -[{rel_type}]-> {target_id} | Powód: {reason}")
                print(f"   [INFO] Relacja zostaje mimo to wymuszona i zapisana w bazie Neo4j.")

            query = f"MATCH (a {{id: $source}}), (b {{id: $target}}) MERGE (a)-[:{rel_type}]->(b)"
            session.run(query, source=source_id, target=target_id)

    driver.close()
    print("Graf zaktualizowany (zastosowano asynchroniczny audyt ontologiczny)!")


if __name__ == "__main__":
    DATA_FOLDER = "data"

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"Stworzono folder '{DATA_FOLDER}'. Wrzuć tam pliki tekstowe (.txt) i uruchom program ponownie.")
        exit()

    pliki = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.txt')]

    if not pliki:
        print(f"Folder '{DATA_FOLDER}' jest pusty. Brak tekstów do wyświetlenia.")
        exit()

    print("\n" + "=" * 15 + " MENU WYBORU PLIKÓW " + "=" * 15)
    for i, plik in enumerate(pliki, 1):
        print(f" [{i}] -> {plik}")
    print("=" * 50)

    wybor_user = input("Wpisz numery plików do przetworzenia oddzielone spacją (np. 1 2 5): ")

    wybrane_indeksy = []
    for element in wybor_user.split():
        if element.isdigit():
            indeks = int(element) - 1
            if 0 <= indeks < len(pliki):
                wybrane_indeksy.append(indeks)

    if not wybrane_indeksy:
        print("Nie wybrano żadnego poprawnego pliku. Koniec programu.")
        exit()

    print(f"\nRozpoczynam sekwencyjne przetwarzanie wybranych plików ({len(wybrane_indeksy)})...")

    for idx in wybrane_indeksy:
        nazwa_pliku = pliki[idx]
        pelna_sciezka = os.path.join(DATA_FOLDER, nazwa_pliku)

        print("\n" + "#" * 30)
        print(f"PRZETWARZAM PLIK: {nazwa_pliku}")
        print("#" * 30)

        try:
            with open(pelna_sciezka, "r", encoding="utf-8") as f:
                tekst_z_pliku = f.read()

            wynik_json = extract_with_gemini(tekst_z_pliku)
            save_to_neo4j(wynik_json)
            print(f"Sukces dla pliku: {nazwa_pliku}")

        except Exception as e:
            print(f"Problem podczas przetwarzania pliku {nazwa_pliku}: {e}")
            print("Przechodzę do kolejnego wybranego zadania...")

    print("\nWszystkie wybrane przez Ciebie pliki zostały pomyślnie obsłużone.")
# Grabbe-Gymnasium Website-Archiv & Content-Pipeline

Dieses Repository enthält alle Scrape-Läufe der alten Grabbe-Gymnasium-
Homepage sowie Werkzeuge zum Vergleich, zur Auswertung und zur Weiterverarbeitung
der Daten für die neue Schulhomepage.

---

## Inhaltsübersicht

```
.
├── scrap_YYYY-MM-DD_HH-MM-SS/   # Scrape-Läufe (je Verzeichnis)
│   ├── www.grabbe-gymnasium.de/ # Heruntergeladene Dateien (kanonisch)
│   ├── scrape-report.json       # Statistiken des Laufs
│   └── sitemap.xml              # Alle entdeckten URLs dieses Laufs
├── scrape.py                    # Scraper v1
├── fast_scrape.py               # Scraper v2 (schnell)
├── scrape_v4.py                 # Scraper v4 (aktuell, empfohlen)
├── verify_scrapes.py            # 🔎 Verifizierung von Fehlerseiten & Duplikaten
├── compare_scrapes.py           # 🔍 Vergleichstool
└── extract_content.py           # 📦 Content-Extraktions-Pipeline
```

---

## Status der Scrape-Läufe

| Lauf | Zeitstempel | URLs gesamt | Heruntergeladen (gemeldet) | Echte Dateien (bereinigt) | Fehler |
|------|-------------|------------|----------------|-----------------------------|--------|
| scrap_2026-03-14_23-33-13 | 2026-03-14 23:33 | 14.399 | 11.902 | **4.458** | ✅ 0 |
| scrap_2026-03-15_09-27-55 | 2026-03-15 09:27 | 14.394 | 11.913 | **4.458** | ✅ 0 |
| scrap_2026-03-15_12-17-08 | 2026-03-15 12:17 | 14.399 | 11.773 | **4.458** | ✅ 0 |
| scrap_2026-03-15_14-07-06 | 2026-03-15 14:07 | 14.843 | 3.589 | 3.572 | ❌ 445 |
| scrap_2026-03-15_14-50-52 | 2026-03-15 14:50 | 15.925 | 3.815 | 3.796 | ❌ 542 |
| scrap_2026-03-15_15-09-40 | 2026-03-15 15:09 | 12.412 | 2.630 | 2.612 | ❌ 510 |

> **Hinweis – Warum unterscheiden sich „gemeldet" und „bereinigt"?**  
> Die hohen gemeldeten Zahlen (~11.900) der ersten drei Läufe waren irreführend:
>
> 1. **„Object not found!"-Fehlerseiten**: Der alte Scraper hat 56 dieser Fehlerseiten heruntergeladen und nicht vollständig vom Disk entfernt.  
> 2. **Domain-Duplikate**: Derselbe Inhalt wurde unter 4 Domain-Verzeichnissen separat gespeichert (`www.grabbe-gymnasium.de/`, `grabbe-gymnasium.de/`, `www.grabbe-gymnasium.info/`, `grabbe-gymnasium.info/`) – **7.151 der ~11.703 Dateien waren redundante Kopien (61 %)**.  
>    Der neue Scraper (v4) konsolidiert alles korrekt unter `www.grabbe-gymnasium.de/` und hinterlässt keine Fehlerseiten.
>
> **→ Empfehlung: `scrap_2026-03-15_09-27-55` als Haupt-Datenquelle verwenden**  
> (4.458 bereinigte echte Dateien, 0 Fehler, keine Duplikate nach Bereinigung).

### Was fehlt im neuesten Lauf?

Gegenüber der Union der drei fehlerfreien Läufe fehlen im neuesten Lauf:

- **2.269 Seiten/HTML-Seiten** (inkl. Fachbereichs-Unterseiten, Newsarchive, etc.)
- **394 Dokumente** (PDFs, Word-Dateien, etc.)
- **1.904 Bilder**
- **33 Medien** (Videos, Audio)
- **270 Assets** (CSS, JS, Fonts)

Die vollständige Liste steht nach Ausführen von `compare_scrapes.py` in
`missing_in_latest.txt` bereit.

---

## Werkzeuge

### 0. `verify_scrapes.py` – Verifizierung von Fehlerseiten & Duplikaten

Prüft alle Scrape-Läufe auf die zwei bekannten Qualitätsprobleme:
- **„Object not found!"-Fehlerseiten** auf Disk (alter Scraper: 56, neuer Scraper: 0)
- **Domain-Duplikate** (alter Scraper: 7.151 redundante Dateikopien = 61 %)

```bash
pip install rich
python verify_scrapes.py
```

### 1. `compare_scrapes.py` – Scrape-Vergleich

Vergleicht alle Scrape-Läufe und erstellt:
- Übersichtstabelle aller Läufe
- Liste der fehlenden URLs im neuesten Lauf (`missing_in_latest.txt`)
- Vereinigte Sitemap aller bekannten URLs (`unified_sitemap.xml`)
- Detaillierter JSON-Bericht (`comparison_report.json`)

```bash
pip install rich
python compare_scrapes.py
```

Optionen:
```
--scrap-dir .       Verzeichnis mit scrap_*-Ordnern (Standard: .)
--output-dir .      Ausgabeverzeichnis für Berichte
--no-unified-sitemap  Keine unified_sitemap.xml erstellen
```

---

### 2. `extract_content.py` – Content-Extraktions-Pipeline

Liest alle HTML-Dateien eines Scrape-Laufs, extrahiert Titel, Beschreibung,
Haupttext, Links und Bilder und speichert alles in:

- **`content.db`** – SQLite-Datenbank mit Volltextsuche (FTS5)
- **`content.jsonl`** – Eine JSON-Zeile pro Seite (ideal für KI-Verarbeitung)

```bash
pip install beautifulsoup4 lxml rich

# Besten Lauf automatisch erkennen und verarbeiten:
python extract_content.py

# Bestimmten Lauf verarbeiten:
python extract_content.py --scrap-run scrap_2026-03-15_09-27-55

# Alle Läufe zusammenführen (dedupliziert):
python extract_content.py --all-runs

# Ausgabe in eigenes Verzeichnis:
python extract_content.py --output-dir ./output
```

#### Datenbank durchsuchen

```bash
# Einfache Suche:
sqlite3 content.db "SELECT url, title FROM pages WHERE content LIKE '%Abitur%';"

# Volltextsuche (FTS5, deutlich schneller):
sqlite3 content.db "SELECT url, title FROM pages_fts WHERE pages_fts MATCH 'Abitur';"

# Alle Seiten eines Bereichs:
sqlite3 content.db "SELECT url, title FROM pages WHERE path LIKE '/cms_hp/musik/%';"

# Statistik:
sqlite3 content.db "SELECT COUNT(*) as Seiten, SUM(word_count) as Wörter FROM pages;"
```

---

## Datenmenge und Struktur

Die drei vollständigen Scrape-Läufe zusammen enthalten ca.:

| Typ | Anzahl |
|-----|--------|
| HTML-Seiten | ~8.500 |
| PDFs und Dokumente | ~1.850 |
| Bilder | ~6.100 |
| Videos/Audio | ~170 |
| Gesamt eindeutige URLs | ~18.300 |

Der extrahierte Textinhalt umfasst ca. **700.000 Wörter** auf ~1.600 Seiten
(nach Filterung von Fehlerseiten und Duplikaten).

---

## Empfohlene Verarbeitung für die neue Homepage

### Schritt 1: Content-Extraktion (lokal, einmalig)

```bash
python extract_content.py --scrap-run scrap_2026-03-15_09-27-55 --output-dir ./output
```

Dies erzeugt `output/content.db` und `output/content.jsonl`.

### Schritt 2: Inhalte sichten und strukturieren

Mit der SQLite-Datenbank lässt sich der gesamte Inhalt bequem durchsuchen,
kategorisieren und in die Struktur der neuen Homepage übertragen.

Empfohlene Kategorisierung nach URL-Pfad:
- `/cms_hp/` – Fachbereichs- und Arbeitsgemeinschafts-Seiten
- `/oberstufe*/` – Oberstufen-Portal
- `/foerderkonzept*/` – Förderkonzept
- `/leitbild*/` – Leitbild der Schule
- `/grabbenachrichten/` – Grabbenachrichten-Archiv
- `/grabbeTV/` – GrabbeTV-Videos

### Schritt 3: KI-gestützte Weiterverarbeitung

Für die eigentliche Textzusammenfassung, Kategorisierung und Migration
in ein neues CMS eignen sich folgende Ansätze:

---

## KI-Agenten und Werkzeuge für die Datenmigration

### Für die Textverarbeitung

| Tool | Stärke | Empfehlung |
|------|--------|------------|
| **[OpenAI GPT-4o](https://platform.openai.com)** | Allgemein, Deutsch sehr gut | Für Umschreiben, Zusammenfassen, Kategorisieren |
| **[Anthropic Claude 3.5 Sonnet](https://claude.ai)** | Sehr lange Dokumente (200k Token) | Für ganze Seiten-Batches auf einmal |
| **[Google Gemini 2.0 Flash](https://aistudio.google.com)** | Schnell, kostengünstig | Für Massenverarbeitung |
| **[Mistral Large](https://mistral.ai)** | Europäischer Anbieter, DSGVO-freundlich | Wenn Datenschutz wichtig ist |

### Für die Daten-Pipeline (RAG / Wissensdatenbank)

| Tool | Beschreibung | Aufwand |
|------|-------------|---------|
| **[LlamaIndex](https://llamaindex.ai)** | Python-Framework, liest JSONL/SQLite direkt | Niedrig |
| **[LangChain](https://langchain.com)** | Flexibles Python-Framework für LLM-Pipelines | Mittel |
| **[Chroma](https://www.trychroma.com)** | Einfache Vektordatenbank (lokal, keine Cloud) | Niedrig |
| **[Weaviate](https://weaviate.io)** | Skalierbare Vektordatenbank | Mittel |
| **[Haystack](https://haystack.deepset.ai)** | Open-Source RAG-Framework | Mittel |

### Für Workflow-Automatisierung

| Tool | Beschreibung |
|------|-------------|
| **[n8n](https://n8n.io)** | Open-Source, selbst hostbar, visuelle Workflows |
| **[Make (ehem. Integromat)](https://make.com)** | Einfach, viele Integrationen |
| **[Zapier](https://zapier.com)** | Einfachste Option, viele Integrationen |

### Für das neue CMS

| Tool | Beschreibung | Empfehlung für Schulen |
|------|-------------|----------------------|
| **[Directus](https://directus.io)** | Headless CMS, SQLite-nativ, selbst hostbar | ⭐ Sehr empfehlenswert |
| **[Strapi](https://strapi.io)** | Populäres Headless CMS, JSON-API | ⭐ Empfehlenswert |
| **[Kirby CMS](https://getkirby.com)** | Datei-basiert, einfach, kein DB nötig | Gut für kleinere Teams |
| **[WordPress](https://wordpress.org)** | Verbreitet, viele Plugins | Nur mit gutem Hosting |
| **[Contao](https://contao.org)** | Deutsch, DSGVO-konform, EU-Hosting | Gut für Behörden/Schulen |

---

## Praktisches Beispiel: Seiten mit LLM zusammenfassen

```python
import json
import openai  # pip install openai

client = openai.OpenAI()  # OPENAI_API_KEY als Umgebungsvariable setzen

with open("output/content.jsonl") as f:
    for line in f:
        page = json.loads(line)
        if page["word_count"] < 50:
            continue  # Zu kurze Seiten überspringen

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du bist Redakteur einer Schulhomepage. "
                 "Fasse den Seiteninhalt kurz und prägnant zusammen."},
                {"role": "user", "content": f"Seite: {page['title']}\n\n{page['content'][:3000]}"},
            ],
            max_tokens=300,
        )
        summary = response.choices[0].message.content
        print(f"URL: {page['url']}")
        print(f"Zusammenfassung: {summary}\n")
```

---

## Praktisches Beispiel: Volltextsuche mit LlamaIndex

```python
# pip install llama-index llama-index-readers-json
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

# JSONL als Dokumente laden
documents = SimpleDirectoryReader(
    input_files=["output/content.jsonl"],
    file_extractor={".jsonl": ...}  # Eigener JSONL-Reader nötig
).load_data()

# Index aufbauen
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# Abfragen
response = query_engine.query("Was sind die Angebote der Oberstufe?")
print(response)
```

---

## Häufige Fragen

**Welchen Scrape-Lauf soll ich für die neue Homepage verwenden?**
→ `scrap_2026-03-15_09-27-55` (4.458 bereinigte echte Dateien, 0 Fehler, kein Duplikat-Problem).

**Ist der neueste Scrape vollständig?**
→ Nein. Er enthält nur ~59 % der bereinigten Dateien des besten Laufs und hat 510 Fehler.
Sieh `missing_in_latest.txt` nach Ausführen von `compare_scrapes.py`.

**Warum meldeten die ersten drei Läufe ~11.900 Downloads, aber nur ~4.500 Dateien sind wirklich einzigartig?**
→ Zwei Gründe: (1) Der alte Scraper speicherte Dateien unter allen 4 Domain-Varianten separat
(7.151 redundante Kopien = 61 %). (2) 56 „Object not found!"-Fehlerseiten verblieben auf Disk.
`verify_scrapes.py` zeigt die vollständige Analyse.

**Wie viele Seiten hat die alte Homepage?**
→ Ca. 4.458 einzigartige Dateien, davon ca. 1.600 HTML-Seiten mit eigenem Textinhalt.

**Wie groß ist der extrahierte Textinhalt?**
→ Ca. 700.000 Wörter auf ~1.600 Seiten. Das entspricht ca. 4–5 Büchern.
Die `content.jsonl`-Datei ist ca. 25 MB groß.

**Kann ich die Daten lokal verarbeiten (ohne Cloud)?**
→ Ja. Mit [Ollama](https://ollama.ai) + [LlamaIndex](https://llamaindex.ai) lässt sich
eine vollständige lokale RAG-Pipeline aufbauen. Empfohlen: `llama3.2` oder `mistral` als Modell.

---

## GitHub Actions Workflows

| Workflow | Datei | Beschreibung |
|----------|-------|-------------|
| Standard-Scrape | `.github/workflows/scrape.yml` | Vollständiger Scrape mit `scrape.py` |
| Fast-Scrape | `.github/workflows/fast_test.yml` | Schneller Scrape mit `fast_scrape.py` |
| Scrape v4 | `.github/workflows/scrape_v4.yml` | Optimierter Scrape mit `scrape_v4.py` |

Alle Workflows erstellen einen neuen Branch (`scrape/*`) und öffnen automatisch
einen Pull Request mit den neuen Scrape-Daten.

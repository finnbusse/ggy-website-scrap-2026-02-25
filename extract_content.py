#!/usr/bin/env python3
"""
extract_content.py – Grabbe-Gymnasium Content-Extraktions-Pipeline
===================================================================
Liest alle heruntergeladenen HTML-Dateien aus einem oder mehreren Scrape-
Läufen, extrahiert relevante Inhalte (Titel, Beschreibung, Haupttext,
Links, Bilder) und speichert sie in:

  • SQLite-Datenbank  (content.db)   – strukturierte Volltextsuche
  • JSONL-Datei       (content.jsonl) – eine JSON-Zeile pro Seite,
                                       ideal für KI-Verarbeitung

Aufruf:
  # Besten Scrape-Lauf verarbeiten (automatisch ermittelt):
  python extract_content.py

  # Bestimmten Scrape-Lauf verarbeiten:
  python extract_content.py --scrap-run scrap_2026-03-15_09-27-55

  # Alle Scrape-Läufe zusammenführen (dedupliziert nach URL):
  python extract_content.py --all-runs

  # Andere Ausgabeverzeichnis:
  python extract_content.py --output-dir ./output

Abhängigkeiten:
  pip install beautifulsoup4 lxml rich
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
    import warnings
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except ImportError:
    print("BeautifulSoup4 fehlt. Bitte installieren: pip install beautifulsoup4 lxml", file=sys.stderr)
    sys.exit(1)

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, MofNCompleteColumn
    RICH = True
except ImportError:
    RICH = False

# HTML-Parser: lxml wenn verfügbar, sonst html.parser
try:
    import lxml  # noqa: F401
    HTML_PARSER = "lxml"
except ImportError:
    HTML_PARSER = "html.parser"

CANONICAL_DOMAIN = "www.grabbe-gymnasium.de"

# Tags, die keine lesbaren Inhalte enthalten
STRIP_TAGS = ["script", "style", "noscript", "meta", "link", "head",
              "nav", "header", "footer", "iframe", "object", "embed"]

# Bekannte CMSimple-CMS Navigations-Texte (werden aus dem Text gefiltert)
CMS_NOISE = re.compile(
    r"Powered by CMSimple|Template:.*?Login|Inhaltsverzeichnis|"
    r"Gesamt-Übersicht|Index A\s*-\s*Z|Login\s*$",
    re.IGNORECASE
)


# ─── Datenbankschema ──────────────────────────────────────────────────────────

CREATE_PAGES_TABLE = """
CREATE TABLE IF NOT EXISTS pages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT    NOT NULL UNIQUE,
    domain      TEXT,
    path        TEXT,
    title       TEXT,
    description TEXT,
    content     TEXT,
    word_count  INTEGER,
    scrape_run  TEXT,
    file_path   TEXT,
    extracted_at TEXT
);
"""

CREATE_FTS_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts
USING fts5(url, title, description, content, content=pages, content_rowid=id);
"""

CREATE_LINKS_TABLE = """
CREATE TABLE IF NOT EXISTS links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    from_url    TEXT NOT NULL,
    to_url      TEXT NOT NULL,
    link_text   TEXT,
    UNIQUE(from_url, to_url)
);
"""

CREATE_IMAGES_TABLE = """
CREATE TABLE IF NOT EXISTS images (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    page_url    TEXT NOT NULL,
    src         TEXT NOT NULL,
    alt         TEXT,
    UNIQUE(page_url, src)
);
"""


# ─── Hilfsfunktionen ──────────────────────────────────────────────────────────

def file_path_to_url(file_path: Path, scrape_root: Path) -> str | None:
    """
    Rekonstruiert die Original-URL aus dem Dateipfad im Scrape-Verzeichnis.

    Rückgabe von None wenn:
      - die Datei nicht unter einem bekannten Domain-Verzeichnis liegt
      - der Pfad leer ist
      - eine unerwartete Ausnahme auftritt

    _Q_-Dekodierung: Der Scraper kodiert ?-URLs (Query-Strings) als
    Dateinamen mit _Q_ als Trennzeichen, z.B.:
      leitbild_Q_TRANSPARENZ.html  →  leitbild?TRANSPARENZ
    Die .html-Erweiterung wird in diesem Fall weggelassen, da die
    originale URL kein .html hatte. Bei normalen .html-Dateien
    (z.B. index.html) bleibt die Erweiterung erhalten.

    Beispiel:
      scrape_root = .../scrap_2026-03-15_09-27-55
      file_path   = .../scrap_2026-03-15_09-27-55/www.grabbe-gymnasium.de/leitbild_Q_TRANSPARENZ.html
      → http://www.grabbe-gymnasium.de/leitbild?TRANSPARENZ
    """
    try:
        rel = file_path.relative_to(scrape_root)
        parts = rel.parts
        if not parts:
            return None
        domain = parts[0]
        if domain not in {
            "grabbe-gymnasium.de", "www.grabbe-gymnasium.de",
            "grabbe-gymnasium.info", "www.grabbe-gymnasium.info",
        }:
            return None
        # Restpfad
        rest = "/".join(parts[1:])
        # Dekodiere _Q_ → ?  (Query-String-Separator)
        # Der Scraper speichert ?-URLs als _Q_-kodierte Dateinamen.
        fname = Path(rest).name
        stem = Path(fname).stem
        decoded_path = rest
        if "_Q_" in stem:
            # Nur beim letzten Segment des Pfads ersetzen;
            # .html-Erweiterung wird ebenfalls entfernt (war nie Teil der echten URL).
            parent = str(Path(rest).parent)
            new_stem = stem.replace("_Q_", "?", 1)
            if parent == ".":
                decoded_path = new_stem
            else:
                decoded_path = parent + "/" + new_stem
        # Normale .html-Dateien behalten ihre Erweiterung, da die originale URL
        # ebenfalls .html hatte (z.B. gg_news05.html).
        url = f"http://{domain}/{decoded_path}"
        return url
    except Exception:
        return None


def extract_page_content(file_path: Path, page_url: str) -> dict:
    """
    Extrahiert Metadaten und Haupttext aus einer HTML-Datei.
    Gibt ein Dictionary mit allen relevanten Feldern zurück.
    """
    html = file_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, HTML_PARSER)

    # ── Fehlerseiten überspringen ──────────────────────────────────────────
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    if "Object not found!" in title or "Fehler 404" in title or "Error 404" in title:
        return {"url": page_url, "skip": True, "reason": "error_page", "title": title}

    # ── Meta-Description ───────────────────────────────────────────────────
    desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    description = desc_tag.get("content", "").strip() if desc_tag else ""

    # ── Hauptinhalt extrahieren ────────────────────────────────────────────
    # CMSimple speichert Inhalte meist direkt im body ohne spezielle Container.
    # Navigationsleisten und Footer werden durch Tag-Entfernung herausgefiltert.
    for tag in soup(STRIP_TAGS):
        tag.decompose()

    # Versuche bekannte Content-Container zu finden
    content_el = (
        soup.find("div", id="content")
        or soup.find("div", id="main")
        or soup.find("main")
        or soup.find("article")
        or soup.find("div", class_=re.compile(r"\bcontent\b", re.I))
        or soup.body
    )

    if not content_el:
        content_text = ""
    else:
        # Leerzeichen normalisieren
        raw_text = content_el.get_text(separator=" ", strip=True)
        # CMS-Rauschen entfernen
        lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
        lines = [ln for ln in lines if not CMS_NOISE.search(ln)]
        content_text = " ".join(lines)
        # Mehrfache Leerzeichen normalisieren
        content_text = re.sub(r"\s{2,}", " ", content_text).strip()

    word_count = len(content_text.split()) if content_text else 0

    # ── Links extrahieren ──────────────────────────────────────────────────
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
            continue
        abs_href = urljoin(page_url, href)
        link_text = a_tag.get_text(strip=True)[:200]
        links.append({"to_url": abs_href, "link_text": link_text})

    # ── Bilder extrahieren ─────────────────────────────────────────────────
    images = []
    for img_tag in soup.find_all("img", src=True):
        src = img_tag["src"].strip()
        if src.startswith("data:"):
            continue
        abs_src = urljoin(page_url, src)
        alt = img_tag.get("alt", "").strip()[:300]
        images.append({"src": abs_src, "alt": alt})

    return {
        "url": page_url,
        "title": title,
        "description": description,
        "content": content_text,
        "word_count": word_count,
        "links": links,
        "images": images,
        "skip": False,
    }


def collect_html_files(run_dir: Path) -> list[Path]:
    """Gibt alle .html-Dateien in einem Scrape-Lauf zurück."""
    html_files = []
    domain_dir = run_dir / CANONICAL_DOMAIN
    if not domain_dir.exists():
        # Fallback: alle HTML-Dateien im run_dir
        domain_dir = run_dir
    for root, _dirs, files in os.walk(domain_dir):
        for fname in files:
            if fname.lower().endswith((".html", ".htm")):
                html_files.append(Path(root) / fname)
    return html_files


# ─── Datenbankoperationen ──────────────────────────────────────────────────────

def init_db(db_path: Path) -> sqlite3.Connection:
    """Erstellt (oder öffnet) die SQLite-Datenbank und initialisiert das Schema."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(
        CREATE_PAGES_TABLE + CREATE_FTS_TABLE + CREATE_LINKS_TABLE + CREATE_IMAGES_TABLE
    )
    conn.commit()
    return conn


def upsert_page(conn: sqlite3.Connection, page: dict, scrape_run: str, file_path: str):
    """Fügt eine Seite in die Datenbank ein oder aktualisiert sie."""
    parsed = urlparse(page["url"])
    conn.execute(
        """
        INSERT INTO pages (url, domain, path, title, description, content,
                           word_count, scrape_run, file_path, extracted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            title=excluded.title,
            description=excluded.description,
            content=excluded.content,
            word_count=excluded.word_count,
            scrape_run=excluded.scrape_run,
            file_path=excluded.file_path,
            extracted_at=excluded.extracted_at
        """,
        (
            page["url"],
            parsed.netloc,
            parsed.path,
            page.get("title", ""),
            page.get("description", ""),
            page.get("content", ""),
            page.get("word_count", 0),
            scrape_run,
            file_path,
            datetime.now().isoformat(),
        ),
    )


def insert_links(conn: sqlite3.Connection, from_url: str, links: list):
    conn.executemany(
        "INSERT OR IGNORE INTO links (from_url, to_url, link_text) VALUES (?, ?, ?)",
        [(from_url, lnk["to_url"], lnk["link_text"]) for lnk in links],
    )


def insert_images(conn: sqlite3.Connection, page_url: str, images: list):
    conn.executemany(
        "INSERT OR IGNORE INTO images (page_url, src, alt) VALUES (?, ?, ?)",
        [(page_url, img["src"], img["alt"]) for img in images],
    )


def rebuild_fts(conn: sqlite3.Connection):
    """Baut den FTS5-Index neu auf."""
    conn.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")
    conn.commit()


# ─── Hauptlogik ───────────────────────────────────────────────────────────────

def process_run(
    run_dir: Path,
    conn: sqlite3.Connection,
    jsonl_file,
    verbose: bool = False,
) -> dict:
    """Verarbeitet einen einzelnen Scrape-Lauf."""
    run_name = run_dir.name
    html_files = collect_html_files(run_dir)

    stats = {"total": len(html_files), "extracted": 0, "skipped": 0, "errors": 0}

    if RICH and not verbose:
        console = Console()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Verarbeite {run_name}", total=len(html_files))
            for fpath in html_files:
                _process_file(fpath, run_dir, run_name, conn, jsonl_file, stats)
                progress.advance(task)
    else:
        for i, fpath in enumerate(html_files, 1):
            if verbose and i % 100 == 0:
                print(f"  {i}/{len(html_files)} Dateien verarbeitet...")
            _process_file(fpath, run_dir, run_name, conn, jsonl_file, stats)

    conn.commit()
    return stats


def _process_file(fpath, run_dir, run_name, conn, jsonl_file, stats):
    """Verarbeitet eine einzelne HTML-Datei."""
    try:
        page_url = file_path_to_url(fpath, run_dir)
        if not page_url:
            stats["skipped"] += 1
            return

        page = extract_page_content(fpath, page_url)

        if page.get("skip"):
            stats["skipped"] += 1
            return

        upsert_page(conn, page, run_name, str(fpath.relative_to(run_dir.parent)))
        if page.get("links"):
            insert_links(conn, page_url, page["links"])
        if page.get("images"):
            insert_images(conn, page_url, page["images"])

        # JSONL-Ausgabe (ohne Links/Images-Listen für kompaktere KI-Verarbeitung)
        jsonl_record = {
            "url": page["url"],
            "title": page.get("title", ""),
            "description": page.get("description", ""),
            "content": page.get("content", ""),
            "word_count": page.get("word_count", 0),
            "scrape_run": run_name,
        }
        jsonl_file.write(json.dumps(jsonl_record, ensure_ascii=False) + "\n")

        stats["extracted"] += 1

    except Exception as e:
        stats["errors"] += 1
        if stats["errors"] <= 5:  # Erste 5 Fehler ausgeben
            print(f"  Fehler bei {fpath}: {e}", file=sys.stderr)


def find_best_run(base_dir: Path) -> Path | None:
    """Ermittelt den besten verfügbaren Scrape-Lauf (meiste Downloads, 0 Fehler)."""
    best = None
    best_dl = -1
    for entry in sorted(base_dir.iterdir()):
        if not (entry.is_dir() and entry.name.startswith("scrap_")):
            continue
        report_path = entry / "scrape-report.json"
        if not report_path.exists():
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        errors = report.get("errors", 0)
        dl = report.get("downloaded", 0)
        if errors == 0 and dl > best_dl:
            best_dl = dl
            best = entry
    return best


def main():
    parser = argparse.ArgumentParser(description="Extrahiert Inhalte aus Scrape-Läufen in SQLite/JSONL.")
    parser.add_argument(
        "--scrap-dir", default=".", help="Verzeichnis mit scrap_*-Ordnern (Standard: .)"
    )
    parser.add_argument(
        "--scrap-run", default=None,
        help="Bestimmten Scrape-Lauf verwenden (Verzeichnisname, z.B. scrap_2026-03-15_09-27-55)"
    )
    parser.add_argument(
        "--all-runs", action="store_true",
        help="Alle Scrape-Läufe zusammenführen (dedupliziert nach URL)"
    )
    parser.add_argument(
        "--output-dir", default=".", help="Ausgabeverzeichnis (Standard: .)"
    )
    parser.add_argument(
        "--db-name", default="content.db", help="Name der SQLite-Datenbank (Standard: content.db)"
    )
    parser.add_argument(
        "--jsonl-name", default="content.jsonl", help="Name der JSONL-Datei (Standard: content.jsonl)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Ausgabe")
    args = parser.parse_args()

    base_dir = Path(args.scrap_dir).resolve()
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    db_path = out_dir / args.db_name
    jsonl_path = out_dir / args.jsonl_name

    # ── Zu verarbeitende Läufe bestimmen ──────────────────────────────────────
    if args.scrap_run:
        run_dir = base_dir / args.scrap_run
        if not run_dir.exists():
            print(f"Fehler: Verzeichnis {run_dir} nicht gefunden.", file=sys.stderr)
            sys.exit(1)
        run_dirs = [run_dir]
    elif args.all_runs:
        run_dirs = sorted(
            [e for e in base_dir.iterdir() if e.is_dir() and e.name.startswith("scrap_")]
        )
        if not run_dirs:
            print("Keine Scrape-Läufe gefunden.", file=sys.stderr)
            sys.exit(1)
    else:
        # Automatisch besten Lauf verwenden
        best = find_best_run(base_dir)
        if not best:
            print("Kein geeigneter Scrape-Lauf gefunden.", file=sys.stderr)
            sys.exit(1)
        run_dirs = [best]
        print(f"Verwende besten Scrape-Lauf: {best.name}")

    # ── Datenbank und JSONL initialisieren ────────────────────────────────────
    conn = init_db(db_path)
    print(f"Datenbank: {db_path}")
    print(f"JSONL-Datei: {jsonl_path}")
    print()

    total_stats = {"total": 0, "extracted": 0, "skipped": 0, "errors": 0}

    with open(jsonl_path, "w", encoding="utf-8") as jsonl_file:
        for run_dir in run_dirs:
            print(f"Verarbeite: {run_dir.name}")
            stats = process_run(run_dir, conn, jsonl_file, verbose=args.verbose)
            for k in total_stats:
                total_stats[k] += stats[k]
            print(
                f"  {stats['extracted']:,} extrahiert, "
                f"{stats['skipped']:,} übersprungen, "
                f"{stats['errors']:,} Fehler"
            )

    # ── FTS-Index aufbauen ────────────────────────────────────────────────────
    print("\nErstelle Volltextindex...")
    rebuild_fts(conn)

    # ── Abschluss-Statistiken ──────────────────────────────────────────────────
    total_pages = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    total_words = conn.execute("SELECT SUM(word_count) FROM pages").fetchone()[0] or 0
    total_links = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    total_images = conn.execute("SELECT COUNT(*) FROM images").fetchone()[0]

    print(f"\n{'='*55}")
    print(f"Extraktion abgeschlossen:")
    print(f"  Seiten in Datenbank: {total_pages:,}")
    print(f"  Gesamtwörter: {total_words:,}")
    print(f"  Links: {total_links:,}")
    print(f"  Bilder: {total_images:,}")
    print(f"  DB-Größe: {db_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"  JSONL-Größe: {jsonl_path.stat().st_size / 1024 / 1024:.1f} MB")
    print()
    print("Nächste Schritte:")
    print("  • SQLite-Suche: sqlite3 content.db \"SELECT url, title FROM pages WHERE content LIKE '%Abitur%'\"")
    print("  • FTS-Suche:    sqlite3 content.db \"SELECT url, title FROM pages_fts WHERE pages_fts MATCH 'Abitur'\"")
    print("  • KI-Verarbeitung: content.jsonl an LLM / RAG-Pipeline übergeben")
    print(f"{'='*55}")

    conn.close()


if __name__ == "__main__":
    main()

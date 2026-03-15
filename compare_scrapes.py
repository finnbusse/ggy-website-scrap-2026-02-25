#!/usr/bin/env python3
"""
compare_scrapes.py – Grabbe-Gymnasium Scrape-Vergleichstool
============================================================
Vergleicht alle vorhandenen Scrape-Läufe miteinander und prüft,
ob im jeweils neuesten Scrape alle relevanten Inhalte vorhanden sind.

Ausgabe:
  • Übersichtstabelle aller Scrape-Läufe
  • Liste der URLs, die im neuesten Lauf fehlen (aufgeteilt nach Typ)
  • unified_sitemap.xml – Vereinigte Sitemap aller bekannten URLs
  • missing_in_latest.txt – Alle fehlenden URLs des neuesten Laufs

Aufruf:
  python compare_scrapes.py [--scrap-dir .]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ─── Optionale Rich-Ausgabe ───────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.table import Table
    from rich import box as rich_box
    RICH = True
except ImportError:
    RICH = False


# ─── Hilfsfunktionen ──────────────────────────────────────────────────────────

def get_urls_from_sitemap(sitemap_path: Path) -> set:
    """Liest alle <loc>-URLs aus einer sitemap.xml."""
    content = sitemap_path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"<loc>(.*?)</loc>", content))


def load_scrape_run(run_dir: Path) -> dict | None:
    """Lädt Bericht und Sitemap eines Scrape-Laufs."""
    report_path = run_dir / "scrape-report.json"
    sitemap_path = run_dir / "sitemap.xml"
    if not report_path.exists() or not sitemap_path.exists():
        return None
    report = json.loads(report_path.read_text(encoding="utf-8"))
    urls = get_urls_from_sitemap(sitemap_path)
    dedup = scan_run_for_dedup(run_dir)
    return {"name": run_dir.name, "report": report, "urls": urls, "path": run_dir, "dedup": dedup}


def classify_url(url: str) -> str:
    """Klassifiziert eine URL nach Inhaltstyp."""
    path = url.split("?")[0].lower().rstrip("/")
    ext = os.path.splitext(path)[1]
    if ext in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods"}:
        return "document"
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".bmp", ".tif", ".tiff"}:
        return "image"
    if ext in {".mp4", ".mp3", ".avi", ".mov", ".wav", ".ogg", ".webm", ".flv"}:
        return "media"
    if ext in {".css", ".js", ".woff", ".woff2", ".ttf", ".eot", ".map"}:
        return "asset"
    if ext in {".html", ".htm", ".php", ""} or "?" in url:
        return "page"
    return "other"


def scan_run_for_dedup(run_dir: Path) -> dict:
    """
    Zaehlt tatsaechliche Dateien je Domain-Verzeichnis und ermittelt
    kreuzdomaenenweite Duplikate und Error-Seiten.

    Gibt zurueck:
      canonical_files    – Dateien in www.grabbe-gymnasium.de/ (kanonisch)
      error_pages_count  – 'Object not found!'-Seiten im kanonischen Verzeichnis
      domain_dirs        – Anzahl vorhandener Domain-Unterverzeichnisse
      extra_copies       – redundante Datei-Kopien durch Mehrfach-Domain-Speicherung
      unique_real_files  – canonical_files minus Error-Seiten
    """
    DOMAIN_DIRS = [
        "www.grabbe-gymnasium.de",
        "grabbe-gymnasium.de",
        "www.grabbe-gymnasium.info",
        "grabbe-gymnasium.info",
    ]
    ERROR_MARKER = "<title>Object not found!</title>"

    from collections import defaultdict
    path_to_domains: dict[str, list] = defaultdict(list)
    canonical_count = 0
    error_count = 0
    domain_dirs_present = 0

    for domain in DOMAIN_DIRS:
        ddir = run_dir / domain
        if not ddir.exists():
            continue
        domain_dirs_present += 1
        for root, _dirs, files in os.walk(ddir):
            for fname in files:
                fpath = Path(root) / fname
                relpath = str(fpath.relative_to(ddir))
                path_to_domains[relpath].append(domain)
                if domain == DOMAIN_DIRS[0]:
                    canonical_count += 1
                    if fname.lower().endswith((".html", ".htm")):
                        try:
                            head = fpath.read_text(encoding="utf-8", errors="replace")[:1500]
                            if ERROR_MARKER in head:
                                error_count += 1
                        except OSError:
                            pass

    extra_copies = sum(len(ds) - 1 for ds in path_to_domains.values() if len(ds) > 1)
    return {
        "canonical_files": canonical_count,
        "error_pages_count": error_count,
        "domain_dirs": domain_dirs_present,
        "extra_copies": extra_copies,
        "unique_real_files": canonical_count - error_count,
    }


def is_error_page_url(url: str) -> bool:
    """Erkennt URLs die bekannte Fehlermuster sind (login, print, sitemap-only)."""
    # &login URLs liefern dasselbe wie die Nicht-Login-Variante
    return url.endswith("&login") or url.endswith("&amp;login")


# ─── Hauptlogik ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Vergleicht alle Scrape-Läufe.")
    parser.add_argument(
        "--scrap-dir", default=".", help="Verzeichnis mit scrap_*-Ordnern (Standard: .)"
    )
    parser.add_argument(
        "--output-dir", default=".", help="Ausgabeverzeichnis für Berichte (Standard: .)"
    )
    parser.add_argument(
        "--no-unified-sitemap", action="store_true",
        help="Keine unified_sitemap.xml erstellen"
    )
    args = parser.parse_args()

    base_dir = Path(args.scrap_dir).resolve()
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Alle Scrape-Läufe einlesen ────────────────────────────────────────────
    runs = []
    for entry in sorted(base_dir.iterdir()):
        if entry.is_dir() and entry.name.startswith("scrap_"):
            run = load_scrape_run(entry)
            if run:
                runs.append(run)

    if not runs:
        print("Keine Scrape-Läufe gefunden.", file=sys.stderr)
        sys.exit(1)

    # ── Zusammenfassung ausgeben ──────────────────────────────────────────────
    if RICH:
        console = Console()
        table = Table(title="Scrape-Übersicht", box=rich_box.ROUNDED)
        table.add_column("Lauf", style="cyan", no_wrap=True)
        table.add_column("Zeitstempel", style="white")
        table.add_column("URLs gesamt", justify="right", style="blue")
        table.add_column("Heruntergeladen\n(gemeldet)", justify="right", style="blue")
        table.add_column("Echte Dateien\n(bereinigt)", justify="right", style="green")
        table.add_column("Fehlerseiten", justify="right", style="red")
        table.add_column("Duplikate\n(extra)", justify="right", style="yellow")
        table.add_column("Fehler", justify="right", style="red")
        table.add_column("Dauer", justify="right")

        for run in runs:
            r = run["report"]
            d = run["dedup"]
            errs = r.get("errors", 0)
            table.add_row(
                run["name"],
                r.get("timestamp", "?")[:19],
                str(r.get("total_urls", "?")),
                str(r.get("downloaded", "?")),
                f"[bold green]{d['unique_real_files']}[/bold green]",
                str(d["error_pages_count"]) if d["error_pages_count"] > 0 else "0",
                str(d["extra_copies"]) if d["extra_copies"] > 0 else "0",
                f"[red]{errs}[/red]" if errs > 0 else "0",
                f"{r.get('duration_seconds', '?')}s",
            )
        console.print(table)
    else:
        print(f"{'Lauf':<35} {'URLs':>8} {'DL(gem)':>8} {'Echt':>6} {'Err-S':>6} {'Dupe':>7} {'Err':>6} {'Dauer':>8}")
        print("-" * 90)
        for run in runs:
            r = run["report"]
            d = run["dedup"]
            print(
                f"{run['name']:<35} "
                f"{r.get('total_urls','?'):>8} "
                f"{r.get('downloaded','?'):>8} "
                f"{d['unique_real_files']:>6} "
                f"{d['error_pages_count']:>6} "
                f"{d['extra_copies']:>7} "
                f"{r.get('errors',0):>6} "
                f"{r.get('duration_seconds','?'):>7}s"
            )

    # ── Referenz-URLs: Union aller "guten" Läufe (0 Fehler) ──────────────────
    good_runs = [r for r in runs if r["report"].get("errors", 0) == 0]
    if not good_runs:
        print("\nKeine Läufe ohne Fehler gefunden – verwende alle Läufe als Referenz.")
        good_runs = runs

    reference_urls: set = set()
    for run in good_runs:
        reference_urls.update(run["urls"])

    # ── Neuester Lauf ─────────────────────────────────────────────────────────
    latest = runs[-1]
    latest_urls = latest["urls"]

    print(f"\nReferenz-URLs (Union aller {len(good_runs)} fehlerfreien Läufe): {len(reference_urls):,}")
    print(f"Neuester Lauf ({latest['name']}): {len(latest_urls):,} URLs")

    # ── Fehlende URLs klassifizieren ──────────────────────────────────────────
    missing = reference_urls - latest_urls
    # Schließe reine &login-Duplikate aus
    missing_content = {u for u in missing if not is_error_page_url(u)}

    by_type: dict[str, list] = {}
    for url in sorted(missing_content):
        t = classify_url(url)
        by_type.setdefault(t, []).append(url)

    total_missing = sum(len(v) for v in by_type.values())
    print(f"\nFehlende URLs im neuesten Lauf (ohne &login-Duplikate): {total_missing:,}")

    type_order = ["page", "document", "image", "media", "asset", "other"]
    for t in type_order:
        urls = by_type.get(t, [])
        if urls:
            label = {
                "page": "Seiten/HTML",
                "document": "Dokumente (PDF etc.)",
                "image": "Bilder",
                "media": "Medien (Video/Audio)",
                "asset": "Assets (CSS/JS/Fonts)",
                "other": "Sonstige",
            }.get(t, t)
            print(f"  {label}: {len(urls):,}")

    # ── Bewertung des neuesten Laufs ──────────────────────────────────────────
    latest_report = latest["report"]
    errs = latest_report.get("errors", 0)
    # Use dedup-corrected unique_real_files for fair comparison
    latest_real = latest["dedup"]["unique_real_files"]
    best_real = max(r["dedup"]["unique_real_files"] for r in good_runs)

    print("\n--- Bewertung des neuesten Scrape-Laufs (bereinigt, ohne Duplikate/Fehlerseiten) ---")
    if errs == 0 and latest_real >= best_real * 0.95:
        print("OK \u2013 VOLLST\u00c4NDIG: Der neueste Scrape ist vergleichbar mit den besten fr\u00fcheren L\u00e4ufen.")
    elif errs == 0:
        pct = latest_real / best_real * 100 if best_real else 0
        print(f"TEILWEISE: {latest_real:,} von ca. {best_real:,} echten Dateien ({pct:.0f}%), 0 Fehler.")
    else:
        pct = latest_real / best_real * 100 if best_real else 0
        print(
            f"UNVOLLST\u00c4NDIG: Nur {latest_real:,} von ca. {best_real:,} echten Dateien ({pct:.0f}%) "
            f"heruntergeladen, {errs:,} Fehler."
        )
        print("   \u2192 Empfehlung: Einen der fr\u00fchen fehlerfreien L\u00e4ufe als Haupt-Datenquelle verwenden.")
        best_run = max(good_runs, key=lambda r: r["dedup"]["unique_real_files"])
        print(f"   \u2192 Bester verf\u00fcgbarer Lauf: {best_run['name']} "
              f"({best_run['dedup']['unique_real_files']:,} echte Dateien, 0 Fehler)")

    # ── Datei: Fehlende URLs ──────────────────────────────────────────────────
    missing_file = out_dir / "missing_in_latest.txt"
    lines = [
        f"# Fehlende URLs im neuesten Scrape-Lauf: {latest['name']}",
        f"# Generiert: {datetime.now().isoformat()[:19]}",
        f"# Referenz: Union aller {len(good_runs)} fehlerfreien Läufe",
        f"# Gesamt fehlend: {total_missing}",
        "",
    ]
    for t in type_order:
        urls = by_type.get(t, [])
        if urls:
            lines.append(f"# === {t.upper()} ({len(urls)}) ===")
            lines.extend(sorted(urls))
            lines.append("")
    missing_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📄  Fehlende URLs gespeichert: {missing_file}")

    # ── Unified Sitemap ───────────────────────────────────────────────────────
    if not args.no_unified_sitemap:
        all_urls: set = set()
        for run in runs:
            all_urls.update(run["urls"])

        sitemap_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        for url in sorted(all_urls):
            safe_url = url.replace("&", "&amp;").replace("&amp;amp;", "&amp;")
            sitemap_lines.append(f"  <url><loc>{safe_url}</loc></url>")
        sitemap_lines.append("</urlset>")

        sitemap_file = out_dir / "unified_sitemap.xml"
        sitemap_file.write_text("\n".join(sitemap_lines), encoding="utf-8")
        print(f"🗺️   Vereinigte Sitemap ({len(all_urls):,} URLs) gespeichert: {sitemap_file}")

    # ── Detaillierter JSON-Bericht ────────────────────────────────────────────
    comparison_report = {
        "generated": datetime.now().isoformat(),
        "runs": [
            {
                "name": r["name"],
                "timestamp": r["report"].get("timestamp"),
                "total_urls": r["report"].get("total_urls"),
                "downloaded_reported": r["report"].get("downloaded"),
                "skipped": r["report"].get("skipped"),
                "errors": r["report"].get("errors"),
                "duration_seconds": r["report"].get("duration_seconds"),
                "url_count": len(r["urls"]),
                "unique_real_files": r["dedup"]["unique_real_files"],
                "error_pages_on_disk": r["dedup"]["error_pages_count"],
                "cross_domain_extra_copies": r["dedup"]["extra_copies"],
                "domain_directories": r["dedup"]["domain_dirs"],
            }
            for r in runs
        ],
        "reference_url_count": len(reference_urls),
        "good_run_count": len(good_runs),
        "latest_run": latest["name"],
        "latest_unique_real_files": latest["dedup"]["unique_real_files"],
        "missing_from_latest": {
            t: sorted(urls) for t, urls in by_type.items()
        },
        "missing_total": total_missing,
        "unified_url_count": len(set().union(*[r["urls"] for r in runs])),
    }
    report_file = out_dir / "comparison_report.json"
    report_file.write_text(
        json.dumps(comparison_report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"📊  Detaillierter Bericht gespeichert: {report_file}")


if __name__ == "__main__":
    main()

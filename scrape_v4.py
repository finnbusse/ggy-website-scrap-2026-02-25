# scrape_v4.py  –  Grabbe-Gymnasium Full-Site Scraper v4
# Optimiert für CMSimple CMS. Ignoriert robots.txt-Restrictions.
# SSL-Verifikation deaktiviert (Schulserver hat oft abgelaufene Zertifikate).
import os, json, time, queue, threading, re, warnings
from datetime import datetime
from urllib.parse import urljoin, urlparse, unquote
from collections import defaultdict

import requests
import urllib3
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, MofNCompleteColumn
from rich.live import Live
from rich.rule import Rule
from rich import box

# Warnungen unterdrücken
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─────────────────────────────────────────────────────────
#  KONFIGURATION
# ─────────────────────────────────────────────────────────
TARGETS = [
    "http://grabbe-gymnasium.de",
    "http://www.grabbe-gymnasium.de",
    "http://grabbe-gymnasium.info",
    "http://www.grabbe-gymnasium.info",
    "https://www.grabbe-gymnasium.info",
]
# Build the allowed-domain set: include both bare and www. variants
_allowed = set()
for _t in TARGETS:
    _n = urlparse(_t).netloc
    _allowed.add(_n)
    _allowed.add("www." + _n if not _n.startswith("www.") else _n[4:])
ALLOWED_DOMAINS  = _allowed
# Canonical domain – all domain variants stored under this single directory
CANONICAL_DOMAIN = "www.grabbe-gymnasium.de"
THREADS          = 24
TIMEOUT          = 15
DELAY            = 0.05
DOWNLOAD_TIMEOUT = (12, 600)
SKIP_EXTENSIONS  = set()

# HTML-Parser: lxml (schnell) mit html.parser als Fallback
try:
    import lxml  # noqa: F401
    HTML_PARSER = "lxml"
except ImportError:
    HTML_PARSER = "html.parser"

# Alle bekannten Seed-Pfade
SEED_PATHS = [
    # CMS-Standard (robots.txt werden NUR als Link-Quellen genutzt, nicht als Restriction)
    "sitemap.xml",
    "sitemap_index.xml",
    "feed.php",
    "robots.txt",
    # Hauptseite-Portale
    "infos/organisation/",
    "infos/unterricht/",
    "cms_hp/nachmittag/",
    "cms_hp/kunst/",
    "cms_hp/musik/",
    "cms_hp/sport/",
    "cms_hp/sport",
    "cms_hp/nawi/",
    "cms_hp/nawi",
    "cms_hp/newsarchiv/",
    "cms_hp/newsarchiv/content/newsOverview.php",
    "foerderkonzept2/",
    "oberstufe2/",
    "leitbild/",
    "kopieretat/",
    "vplan/",
    "vertretung/",
    "cms_hp/",
    # Grabbenachrichten / GG News archive (critical – must be discovered)
    "grabbenachrichten/",
    "grabbenachrichten/gg_news05.html",
    "xpages/grabbenachrichten/",
    "xpages/grabbenachrichten/gg_news05.html",
    # Brute-force all GG News issues (00–99, with and without leading zero)
    *[f"grabbenachrichten/gg_news{i:02d}.html" for i in range(100)],
    *[f"grabbenachrichten/gg_news{i}.html" for i in range(100)],
    *[f"grabbenachrichten/gg_news{i:02d}.htm" for i in range(100)],
    *[f"grabbenachrichten/gg_news{i}.htm" for i in range(100)],
    *[f"xpages/grabbenachrichten/gg_news{i:02d}.html" for i in range(100)],
    *[f"xpages/grabbenachrichten/gg_news{i}.html" for i in range(100)],
    *[f"xpages/grabbenachrichten/gg_news{i:02d}.htm" for i in range(100)],
    *[f"xpages/grabbenachrichten/gg_news{i}.htm" for i in range(100)],
    # GrabbeTV
    "grabbeTV/",
    # Datei-Verzeichnisse
    "userfiles/",
    "userfiles/downloads/",
    "userfiles/downloads/---Anmeldung_Klasse_5/",
    "userfiles/images/",
    # Medien
    "medien/",
    "medien/kalender/",
    "medien/kalender/schuljahresplan.php",
    # Top-Level asset-Pfade
    "downloads/",
    "media/",
    "images/",
    "files/",
    "upload/",
    "uploads/",
    "assets/",
    "js/",
    "css/",
    "templates/",
    "pdf/",
    "audio/",
    "docs/",
    # CMSimple-Query-Seiten (Startseite)
    "?Start",
    "?Dein_Start_in_Klasse_05",
    "?Unser_Profil",
    "?Dein_Start_in_der_Oberstufe",
    "?Unsere_F%C3%A4cher_und_AGs",
    "?Nachmittag",
    "?Wer%2C_was%2C_wo%3F",
    "?Suche",
    "?Impressum",
    "?sitemap=1",
    # Unterportal-Query-Seiten (Organisation)
    "infos/organisation/?Impressum_%2F_Datenschutz",
    "infos/organisation/?Elternbriefe",
    "infos/organisation/?Sekretariat_%2F_Kontakt",
    "infos/organisation/?Schulleitung",
    "infos/organisation/?Kollegium",
    "infos/organisation/?Sch%C3%BClervertretung",
    "infos/organisation/?Elternschaft",
    "infos/organisation/?F%C3%B6rderverein",
    # Unterportal-Query-Seiten (Unterricht)
    "infos/unterricht/?Arbeitsgemeinschaften",
    "infos/unterricht/?Sprachen%2C_Literatur%2C_Kunst%2C_Musik",
    "infos/unterricht/?MINT",
    "infos/unterricht/?Gesellschaft",
    "infos/unterricht/?Religion%2C_Sport",
    "infos/unterricht/?Lehrpl%C3%A4ne_usw.",
    "infos/unterricht/?Stundentafel",
]

# ─────────────────────────────────────────────────────────

console    = Console(highlight=False)
START_TIME = datetime.now()
SCRAP_DIR  = f"./scrap_{START_TIME.strftime('%Y-%m-%d_%H-%M-%S')}"
OUT_DIR    = SCRAP_DIR

_local = threading.local()


def get_session() -> requests.Session:
    """Thread-lokale Session mit Keep-Alive, Retries, OHNE SSL-Verifikation."""
    if not hasattr(_local, "session"):
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        s = requests.Session()
        s.verify = False  # SSL-Zertifikate ignorieren
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=30)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        s.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.5",
        })
        _local.session = s
    return _local.session


def banner():
    console.print(Panel.fit(
        f"[bold cyan]🕷️  Grabbe-Gymnasium Scraper v4[/bold cyan]\n"
        f"[dim]Targets:[/dim] [yellow]{', '.join(TARGETS)}[/yellow]\n"
        f"[dim]Threads:[/dim] [white]{THREADS}[/white]   "
        f"[dim]Delay:[/dim] [white]{DELAY}s[/white]   "
        f"[dim]Parser:[/dim] [white]{HTML_PARSER}[/white]\n"
        f"[dim]Seeds:[/dim]  [white]{len(SEED_PATHS)} extra paths[/white]   "
        f"[dim]SSL verify:[/dim] [red]OFF[/red]\n"
        f"[dim]Started:[/dim] [white]{START_TIME.strftime('%Y-%m-%d %H:%M:%S')}[/white]",
        border_style="cyan", padding=(1, 4)
    ))
    console.print()


# ══════════════════════════════════════════════════════════
#  LINK-EXTRAKTION
# ══════════════════════════════════════════════════════════

_CSS_URL_RE   = re.compile(r"""url\(\s*['"]?([^'"\)\s]+)['"]?\s*\)""", re.I)
_META_REFRESH = re.compile(r"""url=\s*['"]?([^'">\s;]+)""", re.I)
_JS_LOCATION  = re.compile(r"""(?:location\.href|window\.location)\s*=\s*['"]([^'"]+)['"]""", re.I)


def normalise_url(url: str) -> str:
    """Fragment entfernen, Query-Parameter behalten."""
    return urlparse(url)._replace(fragment="").geturl()


def extract_links_from_html(soup: BeautifulSoup, base_url: str) -> set[str]:
    found: set[str] = set()

    def add(href: str):
        if not href:
            return
        href = href.strip()
        if href.startswith(("javascript:", "mailto:", "tel:", "data:", "#")):
            return
        full = normalise_url(urljoin(base_url, href))
        if urlparse(full).netloc in ALLOWED_DOMAINS:
            found.add(full)

    TAG_ATTRS = {
        "a":       ["href"],
        "link":    ["href"],
        "script":  ["src"],
        "img":     ["src", "data-src", "data-lazy-src", "data-original", "data-bg"],
        "source":  ["src"],
        "video":   ["src", "poster"],
        "audio":   ["src"],
        "iframe":  ["src"],
        "frame":   ["src"],
        "embed":   ["src"],
        "object":  ["data"],
        "form":    ["action"],
        "area":    ["href"],
        "input":   ["src"],
        "div":     ["data-src", "data-bg", "data-background"],
        "section": ["data-src", "data-bg", "data-background"],
        "td":      ["background"],
        "table":   ["background"],
        "body":    ["background"],
    }
    for tag_name, attrs in TAG_ATTRS.items():
        for tag in soup.find_all(tag_name):
            for attr in attrs:
                val = tag.get(attr)
                if val:
                    add(val)

    # srcset
    for tag in soup.find_all(attrs={"srcset": True}):
        for part in tag["srcset"].split(","):
            url_part = part.strip().split()[0] if part.strip() else ""
            add(url_part)

    # <meta http-equiv="refresh">
    for tag in soup.find_all("meta", attrs={"http-equiv": re.compile("refresh", re.I)}):
        content = tag.get("content", "")
        m = _META_REFRESH.search(content)
        if m:
            add(m.group(1))

    # og:image, twitter:image, etc.
    for tag in soup.find_all("meta"):
        prop = tag.get("property", "") or tag.get("name", "")
        if "image" in prop.lower() or "url" in prop.lower():
            add(tag.get("content", ""))

    # Inline <style> → url(...)
    for style_tag in soup.find_all("style"):
        for m in _CSS_URL_RE.findall(style_tag.get_text()):
            add(m)

    # style="" Attribut
    for tag in soup.find_all(attrs={"style": True}):
        for m in _CSS_URL_RE.findall(tag["style"]):
            add(m)

    # Inline <script> → location.href / window.location
    for script in soup.find_all("script"):
        text = script.get_text()
        if text:
            for m in _JS_LOCATION.findall(text):
                add(m)

    return found


def extract_links_from_css(css_text: str, base_url: str) -> set[str]:
    found: set[str] = set()
    for href in _CSS_URL_RE.findall(css_text):
        href = href.strip().strip("'\"")
        if not href or href.startswith(("data:", "#")):
            continue
        full = normalise_url(urljoin(base_url, href))
        if urlparse(full).netloc in ALLOWED_DOMAINS:
            found.add(full)
    return found


def extract_links_from_xml(soup: BeautifulSoup) -> set[str]:
    found: set[str] = set()
    for tag in soup.find_all(["loc", "link"]):
        url = tag.get_text(strip=True)
        if not url:
            url = tag.get("href", "")
        url = normalise_url(url.split("#")[0])
        if url and urlparse(url).netloc in ALLOWED_DOMAINS:
            found.add(url)
    return found


def extract_links_from_robots(text: str, base_url: str) -> set[str]:
    """Nur Sitemap-Direktiven extrahieren — Disallow/Allow werden IGNORIERT."""
    found: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("sitemap:"):
            url = line.split(":", 1)[1].strip()
            if urlparse(url).netloc in ALLOWED_DOMAINS:
                found.add(url)
    return found


# ══════════════════════════════════════════════════════════
#  PHASE 1 – CRAWL
# ══════════════════════════════════════════════════════════

def phase1_crawl():
    console.print(Rule("[bold yellow]📡 Phase 1 — Discovery Crawl[/bold yellow]", style="yellow"))
    console.print("[dim]Crawling links (robots.txt restrictions IGNORED)...[/dim]\n")

    visited   = set()
    broken    = []
    by_type   = defaultdict(int)
    lock      = threading.Lock()
    q         = queue.Queue()

    # Seeds
    for t in TARGETS:
        q.put(t)
    for target in TARGETS:
        base = target.rstrip("/")
        for path in SEED_PATHS:
            q.put(f"{base}/{path}")

    stats = {"pages": 0, "assets": 0, "broken": 0, "xml": 0, "css": 0, "current": "–"}

    # Use q.join() + stop event so workers don't exit when queue is temporarily
    # empty while other workers are still processing (and about to enqueue more URLs).
    _stop = threading.Event()
    _done = threading.Event()

    def crawl_worker():
        sess = get_session()
        while not _stop.is_set():
            try:
                url = q.get(timeout=1)
            except queue.Empty:
                continue

            with lock:
                if url in visited:
                    q.task_done()
                    continue
                visited.add(url)

            try:
                r = sess.get(url, timeout=TIMEOUT)
                # Use the final (post-redirect) URL as base for resolving relative links.
                effective_url = r.url
                ct  = r.headers.get("content-type", "").lower()
                path_lower = urlparse(effective_url).path.lower()
                ext = path_lower.rsplit(".", 1)[-1] if "." in path_lower else "html"

                with lock:
                    stats["current"] = url[:75]
                    by_type[ext] += 1

                new_links: set[str] = set()

                is_xml    = any(x in ct for x in ("text/xml", "application/xml",
                                "application/rss+xml", "application/atom+xml",
                                "application/sitemap+xml"))
                is_css    = "text/css" in ct or ext == "css"
                is_html   = "text/html" in ct
                is_robots = path_lower.endswith("robots.txt") and "text/plain" in ct

                if is_robots:
                    new_links = extract_links_from_robots(r.text, effective_url)
                    with lock:
                        stats["pages"] += 1

                elif is_html:
                    # Skip "Object not found!" error pages returned with 200 status
                    if "<title>Object not found!</title>" in r.text[:2048]:
                        with lock:
                            stats["broken"] += 1
                            broken.append(("404-content", url))
                        time.sleep(DELAY)
                        q.task_done()
                        continue

                    soup = BeautifulSoup(r.text, HTML_PARSER)
                    new_links = extract_links_from_html(soup, effective_url)
                    with lock:
                        stats["pages"] += 1

                elif is_xml:
                    try:
                        soup = BeautifulSoup(r.text, "xml")
                    except Exception:
                        soup = BeautifulSoup(r.text, HTML_PARSER)
                    new_links = extract_links_from_xml(soup)
                    with lock:
                        stats["xml"] += 1

                elif is_css:
                    new_links = extract_links_from_css(r.text, effective_url)
                    with lock:
                        stats["css"] += 1

                else:
                    with lock:
                        stats["assets"] += 1

                # Neue Links einreihen
                with lock:
                    for link in new_links:
                        if link not in visited:
                            q.put(link)

                if r.status_code >= 400:
                    with lock:
                        stats["broken"] += 1
                        broken.append((r.status_code, url))

            except Exception:
                with lock:
                    broken.append(("ERR", url))
                    stats["broken"] += 1

            time.sleep(DELAY)
            q.task_done()

    def _queue_watcher():
        q.join()
        _stop.set()
        _done.set()

    watcher = threading.Thread(target=_queue_watcher, daemon=True)
    watcher.start()

    with Live(console=console, refresh_per_second=5) as live:
        threads = [threading.Thread(target=crawl_worker, daemon=True) for _ in range(THREADS)]
        for t in threads:
            t.start()

        while not _done.is_set():
            elapsed_secs = max(1, (datetime.now() - START_TIME).total_seconds())

            with lock:
                visited_count = len(visited)
                pages         = stats["pages"]
                assets        = stats["assets"]
                xml_count     = stats["xml"]
                css_count     = stats["css"]
                broken_count  = stats["broken"]
                current       = stats["current"]

            queue_size = q.qsize()
            speed      = visited_count / elapsed_secs

            grid = Table.grid(expand=True)
            grid.add_column()
            grid.add_column()

            left = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
            left.add_row("[cyan]🌐 URLs visited[/cyan]",   f"[bold white]{visited_count}[/bold white]")
            left.add_row("[cyan]📄 Pages (HTML)[/cyan]",   f"[bold white]{pages}[/bold white]")
            left.add_row("[blue]📋 XML / Feeds[/blue]",    f"[bold white]{xml_count}[/bold white]")
            left.add_row("[yellow]🎨 CSS files[/yellow]",  f"[bold white]{css_count}[/bold white]")
            left.add_row("[magenta]📦 Assets[/magenta]",   f"[bold white]{assets}[/bold white]")
            left.add_row("[red]❌ Broken links[/red]",     f"[bold red]{broken_count}[/bold red]")
            left.add_row("[dim]🔗 Queue remaining[/dim]",  f"[dim]{queue_size}[/dim]")
            left.add_row("[dim]🚀 Speed[/dim]",            f"[dim]{speed:.1f} URLs/s[/dim]")
            left.add_row("[dim]⏱ Elapsed[/dim]",           f"[dim]{int(elapsed_secs)}s[/dim]")

            right = Panel(
                f"[dim]Scanning:[/dim]\n[yellow]{current}[/yellow]",
                title="[bold]🔍 Current URL[/bold]", border_style="dim", width=65
            )

            grid.add_row(left, right)
            live.update(Panel(grid, title="[bold yellow]📡 Discovery Phase[/bold yellow]", border_style="yellow"))
            time.sleep(0.2)

        for t in threads:
            t.join()

    console.print()
    console.print(Rule("[bold green]📊 Discovery Results[/bold green]", style="green"))

    summary_table = Table(box=box.ROUNDED, border_style="green", show_header=True, header_style="bold green")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", justify="right", style="bold white")
    summary_table.add_row("Total URLs found",   str(len(visited)))
    summary_table.add_row("HTML Pages",         str(stats["pages"]))
    summary_table.add_row("XML / Feeds",        str(stats["xml"]))
    summary_table.add_row("CSS Files",          str(stats["css"]))
    summary_table.add_row("Assets (img/pdf/…)", str(stats["assets"]))
    summary_table.add_row("Broken links",       f"[red]{stats['broken']}[/red]")
    console.print(summary_table)
    console.print()

    type_table = Table(title="File Types", box=box.SIMPLE, border_style="dim")
    type_table.add_column("Extension", style="yellow")
    type_table.add_column("Count", justify="right")
    for ext, count in sorted(by_type.items(), key=lambda x: -x[1]):
        type_table.add_row(f".{ext}", str(count))
    console.print(type_table)
    console.print()

    return sorted(visited), broken


# ══════════════════════════════════════════════════════════
#  PHASE 2 – DOWNLOAD
# ══════════════════════════════════════════════════════════

def url_to_path(url: str) -> str:
    parsed = urlparse(url)
    path   = parsed.path.lstrip("/") or "index.html"
    if parsed.query:
        safe_query = re.sub(r'[/\\:*?"<>|&]', '_', unquote(parsed.query))
        if not os.path.splitext(path)[1]:
            path = (path.rstrip("/") or "index") + "_Q_" + safe_query + ".html"
        else:
            path = path + "_Q_" + safe_query
    elif not os.path.splitext(path)[1]:
        path = path.rstrip("/") + "/index.html"
    # Consolidate all domain variants into a single canonical directory
    return os.path.join(OUT_DIR, CANONICAL_DOMAIN, path)


def phase2_download(urls: list[str]):
    console.print(Rule("[bold cyan]⬇️  Phase 2 — Download[/bold cyan]", style="cyan"))

    results   = {"ok": 0, "skip": 0, "err": 0, "current": "–"}
    lock      = threading.Lock()
    url_queue = queue.Queue()
    for u in urls:
        url_queue.put(u)

    def download_worker():
        sess = get_session()
        while True:
            try:
                url = url_queue.get(timeout=3)
            except queue.Empty:
                break

            dest = url_to_path(url)
            with lock:
                results["current"] = url[:70]

            if os.path.exists(dest):
                with lock:
                    results["skip"] += 1
                url_queue.task_done()
                continue

            try:
                ext = os.path.splitext(urlparse(url).path)[1].lower()
                if ext in SKIP_EXTENSIONS:
                    with lock:
                        results["skip"] += 1
                    url_queue.task_done()
                    continue

                r = sess.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)

                # Skip error pages (404, "Object not found!", etc.)
                if r.status_code >= 400:
                    with lock:
                        results["skip"] += 1
                    url_queue.task_done()
                    time.sleep(DELAY)
                    continue

                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=512 * 1024):
                        if chunk:
                            f.write(chunk)

                # Post-download check: remove "Object not found!" error pages
                ct = r.headers.get("content-type", "").lower()
                if "text/html" in ct:
                    try:
                        with open(dest, "r", encoding="utf-8", errors="ignore") as f:
                            head = f.read(2048)
                        if "<title>Object not found!</title>" in head:
                            os.remove(dest)
                            with lock:
                                results["skip"] += 1
                            url_queue.task_done()
                            time.sleep(DELAY)
                            continue
                    except Exception:
                        pass

                with lock:
                    results["ok"] += 1

            except Exception:
                with lock:
                    results["err"] += 1

            time.sleep(DELAY)
            url_queue.task_done()

    total = len(urls)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40),
        MofNCompleteColumn(),
        TextColumn("[dim]{task.fields[status]}"),
        TimeElapsedColumn(),
        console=console,
        refresh_per_second=8,
    ) as progress:

        task = progress.add_task("⬇️  Downloading...", total=total, status="starting…")

        threads = [threading.Thread(target=download_worker, daemon=True) for _ in range(THREADS)]
        for t in threads:
            t.start()

        while any(t.is_alive() for t in threads):
            done = results["ok"] + results["skip"] + results["err"]
            progress.update(task, completed=done,
                status=f"[green]✓{results['ok']}[/green] [dim]⏭{results['skip']}[/dim] [red]✗{results['err']}[/red]  {results['current']}")
            time.sleep(0.15)

        for t in threads:
            t.join()
        progress.update(task, completed=total)

    return results


# ══════════════════════════════════════════════════════════
#  SITEMAP
# ══════════════════════════════════════════════════════════

def generate_sitemap(urls: list[str], scrap_dir: str):
    os.makedirs(scrap_dir, exist_ok=True)
    sitemap_path = os.path.join(scrap_dir, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in sorted(urls):
            escaped = url.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            f.write(f"  <url><loc>{escaped}</loc></url>\n")
        f.write("</urlset>\n")
    console.print(f"[dim]Sitemap: {sitemap_path} ({len(urls)} URLs)[/dim]")


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    banner()

    all_urls, broken = phase1_crawl()

    os.makedirs(SCRAP_DIR, exist_ok=True)
    generate_sitemap(all_urls, SCRAP_DIR)
    generate_sitemap(all_urls, ".")  # also write to repo root for git history

    console.print(Panel(
        f"[bold]Gefunden: [cyan]{len(all_urls)}[/cyan] URLs.[/bold]\n"
        f"Download nach [yellow]{SCRAP_DIR}/[/yellow]…",
        border_style="cyan", title="[bold]Ready to Download[/bold]"
    ))
    console.print()

    dl = phase2_download(all_urls)

    elapsed = str(datetime.now() - START_TIME).split(".")[0]
    console.print()
    console.print(Rule("[bold green]✅ Complete[/bold green]", style="green"))

    final = Table(box=box.ROUNDED, border_style="green")
    final.add_column("", style="cyan")
    final.add_column("", justify="right", style="bold white")
    final.add_row("Total URLs crawled",   str(len(all_urls)))
    final.add_row("✅ Downloaded",         f"[green]{dl['ok']}[/green]")
    final.add_row("⏭️  Skipped",           str(dl["skip"]))
    final.add_row("❌ Errors",             f"[red]{dl['err']}[/red]")
    final.add_row("⏱️  Total time",        elapsed)
    console.print(final)

    report = {
        "timestamp":        START_TIME.isoformat(),
        "scrap_dir":        SCRAP_DIR,
        "targets":          TARGETS,
        "threads":          THREADS,
        "seed_paths":       len(SEED_PATHS),
        "total_urls":       len(all_urls),
        "downloaded":       dl["ok"],
        "skipped":          dl["skip"],
        "errors":           dl["err"],
        "broken_links":     broken[:200],
        "duration_seconds": int((datetime.now() - START_TIME).total_seconds()),
    }
    report_path = os.path.join(SCRAP_DIR, "scrape-report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    with open("scrape-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    console.print(f"\n[dim]Report: {report_path} & scrape-report.json[/dim]")
    console.print(f"[bold green]Fertig! Mirror in {SCRAP_DIR}/[/bold green]\n")

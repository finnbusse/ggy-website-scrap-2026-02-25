# fast_scrape.py – speed-optimised copy of scrape.py
#
# Key changes vs. scrape.py:
#   • THREADS 6 → 32   – I/O-bound work scales almost linearly with threads
#   • DELAY   0.3 → 0  – remove artificial polite-crawl pause
#   • Per-thread requests.Session with HTTP keep-alive & connection pooling
#     (eliminates TCP-handshake overhead on every request)
#   • Connect timeout 15 s → 8 s  (fail faster on dead/slow hosts)
#   • Download chunk size 1 MB → 4 MB  (fewer syscalls per large file)
import os, json, time, queue, threading, re, warnings
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import defaultdict

import requests
import requests.adapters
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, MofNCompleteColumn
from rich.live import Live
from rich.rule import Rule
from rich import box

# Suppress warning when lxml accidentally sees XML served without proper content-type
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# ─────────────────────────────────────────
# A realistic Firefox UA so servers don't block or serve degraded content.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
    "Gecko/20100101 Firefox/124.0"
)

TARGETS = [
    "http://grabbe-gymnasium.de",
    "http://www.grabbe-gymnasium.de",
    "http://grabbe-gymnasium.info",
    "http://www.grabbe-gymnasium.info",
    "https://www.grabbe-gymnasium.info",
]

# Build the allowed-domain set: include both bare and www. variants of every
# target host so that links like https://www.grabbe-gymnasium.info/... are
# followed even when the target was seeded as grabbe-gymnasium.info.
def _build_allowed_domains(targets):
    domains = set()
    for t in targets:
        netloc = urlparse(t).netloc
        domains.add(netloc)
        # Ensure both www. and bare version are always accepted
        if netloc.startswith("www."):
            domains.add(netloc[4:])
        else:
            domains.add("www." + netloc)
    return domains

ALLOWED_DOMAINS  = _build_allowed_domains(TARGETS)
THREADS          = 48                  # ↑ was 6  – I/O-bound benefits from many threads
TIMEOUT          = 8                   # ↓ was 15 – connect timeout only; fail fast on dead hosts
DELAY            = 0                   # ↓ was 0.3 – no artificial pause
DOWNLOAD_TIMEOUT = (8, 600)            # (connect, read) – connect faster; keep long read for large files
SKIP_EXTENSIONS  = set()

# CMSimple CMS – extra seed paths to probe on every target host.
CMSIMPLE_EXTRA_PATHS = [
    "sitemap.xml",
    "sitemap_index.xml",
    "feed.php",
    "robots.txt",
    "userfiles/",
    "cms_hp/",
]
# ─────────────────────────────────────────

console = Console(highlight=False)
START_TIME = datetime.now()
SCRAP_DIR  = f"./scrap_{START_TIME.strftime('%Y-%m-%d_%H-%M-%S')}"
OUT_DIR    = SCRAP_DIR

# ─────────────────────────────────────────
# Per-thread requests.Session with HTTP keep-alive and a large connection pool.
# Sessions are NOT shared across threads to avoid locking on cookie state.
_thread_local = threading.local()

def _get_session() -> requests.Session:
    """Return (or lazily create) a per-thread Session with connection pooling."""
    if not hasattr(_thread_local, "session"):
        s = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=THREADS,    # one connection pool per origin
            pool_maxsize=THREADS,        # one slot per thread – no contention
            max_retries=0,
        )
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        s.headers.update({"User-Agent": USER_AGENT})
        _thread_local.session = s
    return _thread_local.session
# ─────────────────────────────────────────

def banner():
    console.print(Panel.fit(
        f"[bold cyan]🕷️  School Website Scraper – FAST MODE[/bold cyan]\n"
        f"[dim]Targets:[/dim] [yellow]{', '.join(TARGETS)}[/yellow]\n"
        f"[dim]Started:[/dim] [white]{START_TIME.strftime('%Y-%m-%d %H:%M:%S')}[/white]\n"
        f"[dim]Threads:[/dim] [bold white]{THREADS}[/bold white]  "
        f"[dim]Delay:[/dim] [bold white]{DELAY}s[/bold white]  "
        f"[dim]Timeout:[/dim] [bold white]{TIMEOUT}s[/bold white]",
        border_style="cyan", padding=(1, 4)
    ))
    console.print()

# ══════════════════════════════════════════════════════════
#  PHASE 1 – CRAWL
# ══════════════════════════════════════════════════════════

def phase1_crawl():
    console.print(Rule("[bold yellow]📡 Phase 1 — Discovery Crawl[/bold yellow]", style="yellow"))
    console.print("[dim]Crawling all links first — no downloads yet...[/dim]\n")

    visited  = set()
    broken   = []
    by_type  = defaultdict(int)
    lock     = threading.Lock()
    q        = queue.Queue()

    # Seed the queue with the main targets
    for t in TARGETS:
        q.put(t)

    # CMSimple CMS – probe extra paths known to exist on CMSimple installations
    for target in TARGETS:
        base = target.rstrip("/")
        for path in CMSIMPLE_EXTRA_PATHS:
            q.put(f"{base}/{path}")

    stats = {"pages": 0, "assets": 0, "broken": 0, "xml": 0, "current": "–"}

    # Use q.join() + stop event so workers never exit due to a transient empty
    # queue while other workers are still processing (and about to enqueue more
    # URLs).  All threads stay busy right until all reachable URLs are done.
    _stop = threading.Event()
    _done = threading.Event()

    def crawl_worker():
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
                r = _get_session().get(url, timeout=TIMEOUT, allow_redirects=True)
                # Use the final URL after redirects as the base for resolving
                # relative links – this is crucial when a bare domain redirects
                # to its www. counterpart.
                effective_url = r.url
                ct = r.headers.get("content-type", "").lower()
                ext = urlparse(url).path.split(".")[-1].lower() if "." in urlparse(url).path else "html"

                with lock:
                    stats["current"] = url[:70]
                    by_type[ext] += 1

                # Choose the right parser: lxml for HTML, lxml-xml for XML/Atom/RSS
                is_xml = any(x in ct for x in ("text/xml", "application/xml",
                                                "application/rss+xml", "application/atom+xml",
                                                "application/sitemap+xml"))
                is_css = "text/css" in ct

                def _enqueue(raw):
                    """Resolve *raw* against effective_url and enqueue if internal."""
                    if not raw:
                        return
                    full = urljoin(effective_url, raw.strip()).split("#")[0]
                    if not full:
                        return
                    if urlparse(full).netloc in ALLOWED_DOMAINS:
                        with lock:
                            if full not in visited:
                                q.put(full)

                def _enqueue_css_urls(css_text):
                    """Extract all url(...) references from a CSS string."""
                    for m in re.finditer(r'url\(\s*["\']?([^)"\']+?)["\']?\s*\)', css_text):
                        _enqueue(m.group(1))

                if is_css:
                    with lock:
                        stats["assets"] += 1
                    _enqueue_css_urls(r.text)

                elif "text/html" in ct or is_xml:
                    parser = "xml" if is_xml else "lxml"
                    with lock:
                        if is_xml:
                            stats["xml"] += 1
                        else:
                            stats["pages"] += 1
                    soup = BeautifulSoup(r.text, parser)

                    if is_xml:
                        for loc in soup.find_all("loc"):
                            full = loc.get_text(strip=True).split("#")[0]
                            if urlparse(full).netloc in ALLOWED_DOMAINS:
                                with lock:
                                    if full not in visited:
                                        q.put(full)
                    else:
                        # ── Tag / attribute scan ─────────────────────────────
                        TAG_ATTRS = [
                            (["a", "area", "link"],
                             ["href"]),
                            (["script", "img", "audio", "video", "source",
                              "track", "embed", "iframe", "frame", "input",
                              "button"],
                             ["src", "data-src", "data-href"]),
                            (["video"],          ["poster"]),
                            (["object"],         ["data"]),
                            (["form"],           ["action"]),
                            (["blockquote", "ins", "del", "q"], ["cite"]),
                        ]
                        for tags, attrs in TAG_ATTRS:
                            for tag in soup.find_all(tags):
                                for attr in attrs:
                                    _enqueue(tag.get(attr))
                                # srcset="img.png 1x, img@2x.png 2x"
                                srcset = tag.get("srcset", "")
                                if srcset:
                                    for part in srcset.split(","):
                                        _enqueue(part.strip().split()[0])

                        # ── <style> blocks ───────────────────────────────────
                        for style_tag in soup.find_all("style"):
                            _enqueue_css_urls(style_tag.get_text())

                        # ── inline style="" attributes ───────────────────────
                        for tag in soup.find_all(style=True):
                            _enqueue_css_urls(tag["style"])

                        # ── <meta http-equiv="refresh"> ──────────────────────
                        for meta in soup.find_all(
                                "meta",
                                attrs={"http-equiv": re.compile(r"^refresh$", re.I)}):
                            content = meta.get("content", "")
                            m = re.search(r'url\s*=\s*["\']?([^\s;"\']+)', content, re.I)
                            if m:
                                _enqueue(m.group(1))

                        # ── URLs embedded in <script> text ───────────────────
                        for script in soup.find_all("script"):
                            js = script.get_text()
                            # Absolute internal URLs
                            for m in re.finditer(
                                    r'["\']((https?://)?' + r'|'.join(
                                        re.escape(d) for d in ALLOWED_DOMAINS
                                    ) + r'[^"\']+)["\']', js):
                                _enqueue(m.group(1))
                            # Quoted relative paths that look like pages/assets
                            for m in re.finditer(
                                    r'["\'](/[^"\'?\s]{2,}(?:\?[^"\']*)?)["\']', js):
                                _enqueue(m.group(1))
                else:
                    with lock:
                        stats["assets"] += 1

                if r.status_code >= 400:
                    with lock:
                        stats["broken"] += 1
                        broken.append((r.status_code, url))

            except Exception:
                with lock:
                    broken.append(("ERR", url))
                    stats["broken"] += 1

            q.task_done()

    def _queue_watcher():
        q.join()        # blocks until every task_done() has been called
        _stop.set()
        _done.set()

    watcher = threading.Thread(target=_queue_watcher, daemon=True)
    watcher.start()

    with Live(console=console, refresh_per_second=4) as live:
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
            left.add_row("[magenta]📦 Assets[/magenta]",   f"[bold white]{assets}[/bold white]")
            left.add_row("[red]❌ Broken links[/red]",     f"[bold red]{broken_count}[/bold red]")
            left.add_row("[dim]🔗 Queue remaining[/dim]",  f"[dim]{queue_size}[/dim]")
            left.add_row("[dim]🚀 Speed[/dim]",            f"[dim]{speed:.1f} URLs/s[/dim]")
            left.add_row("[dim]⏱ Elapsed[/dim]",           f"[dim]{int(elapsed_secs)}s[/dim]")

            right = Panel(
                f"[dim]Scanning:[/dim]\n[yellow]{current}[/yellow]",
                title="[bold]🔍 Current URL[/bold]", border_style="dim", width=60
            )

            grid.add_row(left, right)
            live.update(Panel(grid, title="[bold yellow]📡 Discovery Phase[/bold yellow]", border_style="yellow"))
            time.sleep(0.25)

        for t in threads:
            t.join()

    console.print()
    console.print(Rule("[bold green]📊 Discovery Results[/bold green]", style="green"))

    summary = Table(box=box.ROUNDED, border_style="green", show_header=True, header_style="bold green")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", justify="right", style="bold white")
    summary.add_row("Total URLs found",   str(len(visited)))
    summary.add_row("HTML Pages",         str(stats["pages"]))
    summary.add_row("XML / Feeds",        str(stats["xml"]))
    summary.add_row("Assets (img/pdf/…)", str(stats["assets"]))
    summary.add_row("Broken links",       f"[red]{stats['broken']}[/red]")
    console.print(summary)
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

def url_to_path(url):
    parsed = urlparse(url)
    path = parsed.path.lstrip("/") or "index.html"
    if parsed.query:
        safe_query = re.sub(r'[/\\:*?"<>|]', '_', parsed.query)
        if not os.path.splitext(path)[1]:
            path = (path.rstrip("/") or "index") + "_Q_" + safe_query + ".html"
        else:
            path = path + "_Q_" + safe_query
    elif not os.path.splitext(path)[1]:
        path = path.rstrip("/") + "/index.html"
    return os.path.join(OUT_DIR, parsed.netloc, path)

def phase2_download(urls):
    console.print(Rule("[bold cyan]⬇️  Phase 2 — Download[/bold cyan]", style="cyan"))

    results = {"ok": 0, "skip": 0, "err": 0, "current": "–"}
    lock = threading.Lock()
    url_queue = queue.Queue()
    for u in urls:
        url_queue.put(u)

    def download_worker():
        while True:
            try:
                url = url_queue.get(timeout=2)
            except queue.Empty:
                break

            dest = url_to_path(url)
            with lock:
                results["current"] = url[:65]

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

                # Stream download so large files (100 MB+) don't time out.
                # 4 MB chunks reduce syscall overhead vs. 1 MB.
                r = _get_session().get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
                        f.write(chunk)
                with lock:
                    results["ok"] += 1

            except Exception:
                with lock:
                    results["err"] += 1

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
        refresh_per_second=6,
    ) as progress:

        task = progress.add_task("⬇️  Downloading...", total=total, status="starting…")

        threads = [threading.Thread(target=download_worker, daemon=True) for _ in range(THREADS)]
        for t in threads:
            t.start()

        while any(t.is_alive() for t in threads):
            done = results["ok"] + results["skip"] + results["err"]
            progress.update(task, completed=done,
                status=f"[green]✓{results['ok']}[/green] [dim]⏭{results['skip']}[/dim] [red]✗{results['err']}[/red]  {results['current']}")
            time.sleep(0.2)

        for t in threads:
            t.join()
        progress.update(task, completed=total)

    return results

# ══════════════════════════════════════════════════════════
#  SITEMAP GENERATOR
# ══════════════════════════════════════════════════════════

def generate_sitemap(urls, scrap_dir):
    """Write a standard sitemap.xml listing every discovered URL."""
    os.makedirs(scrap_dir, exist_ok=True)
    sitemap_path = os.path.join(scrap_dir, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in sorted(urls):
            escaped = url.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            f.write(f"  <url><loc>{escaped}</loc></url>\n")
        f.write("</urlset>\n")
    console.print(f"[dim]Sitemap saved to {sitemap_path} ({len(urls)} URLs)[/dim]")

# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    banner()

    all_urls, broken = phase1_crawl()

    os.makedirs(SCRAP_DIR, exist_ok=True)
    generate_sitemap(all_urls, SCRAP_DIR)
    generate_sitemap(all_urls, ".")

    console.print(Panel(
        f"[bold]Found [cyan]{len(all_urls)}[/cyan] URLs total.[/bold]\n"
        f"Proceeding to download all files into [yellow]{SCRAP_DIR}/[/yellow]…",
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
        "timestamp": START_TIME.isoformat(),
        "scrap_dir": SCRAP_DIR,
        "targets": TARGETS,
        "allowed_domains": sorted(ALLOWED_DOMAINS),
        "total_urls": len(all_urls),
        "downloaded": dl["ok"],
        "skipped": dl["skip"],
        "errors": dl["err"],
        "broken_links": broken[:50],
        "duration_seconds": int((datetime.now() - START_TIME).total_seconds()),
    }
    report_path = os.path.join(SCRAP_DIR, "scrape-report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    with open("scrape-report.json", "w") as f:
        json.dump(report, f, indent=2)

    console.print(f"\n[dim]Report saved to {report_path} and scrape-report.json[/dim]")
    console.print(f"[bold green]All done! Results in {SCRAP_DIR}/[/bold green]\n")

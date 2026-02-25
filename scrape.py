# scrape.py
import os, re, json, time, queue, threading, mimetypes
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, MofNCompleteColumn
from rich.live import Live
from rich.rule import Rule
from rich import box

# ─────────────────────────────────────────
TARGET     = "https://grabbe-gymnasium.de"
OUT_DIR    = "./mirror"
THREADS    = 6
TIMEOUT    = 15
DELAY      = 0.3
# ─────────────────────────────────────────

console = Console(highlight=False)
START_TIME = datetime.now()

def banner():
    console.print(Panel.fit(
        f"[bold cyan]🕷️  School Website Scraper[/bold cyan]\n"
        f"[dim]Target:[/dim] [yellow]{TARGET}[/yellow]\n"
        f"[dim]Started:[/dim] [white]{START_TIME.strftime('%Y-%m-%d %H:%M:%S')}[/white]",
        border_style="cyan", padding=(1, 4)
    ))
    console.print()

# ══════════════════════════════════════════════════════════
#  PHASE 1 – CRAWL
# ══════════════════════════════════════════════════════════

def phase1_crawl():
    console.print(Rule("[bold yellow]📡 Phase 1 — Discovery Crawl[/bold yellow]", style="yellow"))
    console.print("[dim]Crawling all links first — no downloads yet...[/dim]\n")

    visited   = set()
    to_visit  = {TARGET}
    assets    = set()
    broken    = []
    by_type   = defaultdict(int)
    lock      = threading.Lock()
    q         = queue.Queue()
    q.put(TARGET)

    stats = {"pages": 0, "assets": 0, "broken": 0, "current": "–"}

    def crawl_worker():
        while True:
            try:
                url = q.get(timeout=2)
            except queue.Empty:
                break

            with lock:
                if url in visited:
                    q.task_done()
                    continue
                visited.add(url)

            try:
                r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0 (compatible; SchoolScraper/1.0)"})
                ct = r.headers.get("content-type", "")
                ext = urlparse(url).path.split(".")[-1].lower() if "." in urlparse(url).path else "html"

                with lock:
                    stats["current"] = url.replace(TARGET, "")[:70] or "/"
                    by_type[ext] += 1

                if "text/html" in ct:
                    with lock:
                        stats["pages"] += 1
                    soup = BeautifulSoup(r.text, "lxml")
                    for tag in soup.find_all(["a", "link", "script", "img"]):
                        href = tag.get("href") or tag.get("src") or ""
                        full = urljoin(url, href).split("#")[0].split("?")[0]
                        if not full.startswith(TARGET):
                            continue
                        with lock:
                            if full not in visited:
                                q.put(full)
                else:
                    with lock:
                        stats["assets"] += 1
                        assets.add(url)

                if r.status_code >= 400:
                    with lock:
                        stats["broken"] += 1
                        broken.append((r.status_code, url))

            except Exception as e:
                with lock:
                    broken.append(("ERR", url))
                    stats["broken"] += 1

            time.sleep(DELAY)
            q.task_done()

    with Live(console=console, refresh_per_second=4) as live:
        threads = [threading.Thread(target=crawl_worker, daemon=True) for _ in range(THREADS)]
        for t in threads:
            t.start()

        while any(t.is_alive() for t in threads):
            elapsed = (datetime.now() - START_TIME).seconds

            grid = Table.grid(expand=True)
            grid.add_column()
            grid.add_column()

            left = Table(box=box.SIMPLE, show_header=False, padding=(0,1))
            left.add_row("[cyan]📄 Pages found[/cyan]",        f"[bold white]{stats['pages']}[/bold white]")
            left.add_row("[magenta]📦 Assets found[/magenta]", f"[bold white]{stats['assets']}[/bold white]")
            left.add_row("[red]❌ Broken links[/red]",         f"[bold red]{stats['broken']}[/bold red]")
            left.add_row("[dim]⏱ Elapsed[/dim]",               f"[dim]{elapsed}s[/dim]")

            right = Panel(
                f"[dim]Scanning:[/dim]\n[yellow]{stats['current']}[/yellow]",
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
    summary.add_row("Total URLs found",           str(len(visited)))
    summary.add_row("HTML Pages",                 str(stats["pages"]))
    summary.add_row("Assets (img/pdf/css/…)",     str(stats["assets"]))
    summary.add_row("Broken links",               f"[red]{stats['broken']}[/red]")
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
    if not os.path.splitext(path)[1]:
        path = path.rstrip("/") + "/index.html"
    return os.path.join(OUT_DIR, parsed.netloc, path)

def phase2_download(urls):
    console.print(Rule("[bold cyan]⬇️  Phase 2 — Download[/bold cyan]", style="cyan"))

    results = {"ok": 0, "skip": 0, "err": 0, "current": "–", "last_saved": "–"}
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
                results["current"] = url.replace(TARGET, "")[:65] or "/"

            if os.path.exists(dest):
                with lock:
                    results["skip"] += 1
                url_queue.task_done()
                time.sleep(DELAY)
                continue

            try:
                r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                mode = "w" if "text" in r.headers.get("content-type", "") else "wb"
                content = r.text if mode == "w" else r.content
                with open(dest, mode, encoding="utf-8" if mode == "w" else None) as f:
                    f.write(content)
                with lock:
                    results["ok"] += 1
                    results["last_saved"] = os.path.basename(dest)
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
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    banner()

    all_urls, broken = phase1_crawl()

    console.print(Panel(
        f"[bold]Found [cyan]{len(all_urls)}[/cyan] URLs total.[/bold]\n"
        f"Proceeding to download all files into [yellow]./mirror/[/yellow]…",
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
    final.add_row("Total URLs crawled",    str(len(all_urls)))
    final.add_row("✅ Downloaded",          f"[green]{dl['ok']}[/green]")
    final.add_row("⏭️  Skipped (cached)",   str(dl["skip"]))
    final.add_row("❌ Errors",              f"[red]{dl['err']}[/red]")
    final.add_row("⏱️  Total time",         elapsed)
    console.print(final)

    report = {
        "timestamp": START_TIME.isoformat(),
        "target": TARGET,
        "total_urls": len(all_urls),
        "downloaded": dl["ok"],
        "skipped": dl["skip"],
        "errors": dl["err"],
        "broken_links": broken[:50],
        "duration_seconds": (datetime.now() - START_TIME).seconds
    }
    with open("scrape-report.json", "w") as f:
        json.dump(report, f, indent=2)

    console.print("\n[dim]Report saved to scrape-report.json[/dim]")
    console.print(f"[bold green]All done! Mirror in ./mirror/[/bold green]\n")

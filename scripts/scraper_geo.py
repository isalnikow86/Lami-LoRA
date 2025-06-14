
import requests
from bs4 import BeautifulSoup
import json

GEO_START_PATHS = [
    "/geolino/tierlexikon/",
    "/geolino/redewendungen/",
    "/geolino/berufe/"
]

GEO_BASE = "https://www.geo.de"


def collect_geo_links(start_path):
    try:
        res = requests.get(GEO_BASE + start_path, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a.get("href") for a in soup.find_all("a", href=True)]
        return [l for l in links if l and l.startswith(start_path)]
    except Exception as e:
        print(f"❌ Fehler beim Abrufen von {start_path}: {e}")
        return []


def scrape_geo_article(url):
    try:
        full_url = url if url.startswith("http") else GEO_BASE + url
        res = requests.get(full_url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.title.text.strip() if soup.title else "Kein Titel"
        content_tag = soup.find("div", class_="c-article-text")
        if content_tag:
            text = content_tag.get_text(separator="\n").strip()
            if len(text) > 200:
                return {"url": full_url, "title": title, "text": text}
    except Exception as e:
        print(f"⚠ Fehler bei {url}: {e}")
    return None


def run_scraper():
    print("\n▶ Starte GEO-Scraper...")
    all_articles = []
    visited = set()
    for path in GEO_START_PATHS:
        print(f"\n🔍 Scanne Bereich: {path}")
        links = collect_geo_links(path)
        print(f"🔗 {len(links)} Links gefunden")
        for link in links:
            if link in visited:
                continue
            visited.add(link)
            article = scrape_geo_article(link)
            if article:
                all_articles.append(article)
                print(f"✅ {article['title']}")

    with open("data/geo_texts.jsonl", "w") as f:
        for item in all_articles:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ GEO-Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → data/geo_texts.jsonl")


if __name__ == "__main__":
    run_scraper()

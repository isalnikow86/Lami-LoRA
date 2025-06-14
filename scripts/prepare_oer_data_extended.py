import requests
from bs4 import BeautifulSoup
import json
import time

OER_SOURCES = [
    {
        "name": "kindersache",
        "base_url": "https://www.kindersache.de",
        "start_path": "/bereiche/wissen/natur-und-mensch",
        "article_selector": "div.view-content a",
        "content_selector": "div.field--name-body"
    },
    {
        "name": "hanisauland",
        "base_url": "https://www.hanisauland.de",
        "start_path": "/wissen/lexikon/grosses-lexikon/a",
        "article_selector": "ul.linklist__list a",
        "content_selector": "div.text"
    },
    {
        "name": "geo",
        "base_url": "https://www.geo.de",
        "start_paths": [
            "/geolino/tierlexikon",
            "/geolino/mensch"
        ],
        "article_selector": "a.m-teaser",
        "content_selector": "div.c-article-text"
    }
]

def scrape_articles(source):
    articles = []
    visited = set()
    counter = 0

    def scrape_page(url):
        nonlocal counter
        try:
            full_url = url if url.startswith("http") else source["base_url"] + url
            if full_url in visited:
                return
            visited.add(full_url)

            # Duplikate durch Paginierung ignorieren
            if "?page=" in full_url:
                return

            res = requests.get(full_url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            content = soup.select_one(source["content_selector"])
            if not content:
                return

            title = soup.title.text.strip() if soup.title else "No title"
            text = content.get_text(separator="\n").strip()

            if len(text) > 200:
                articles.append({
                    "url": full_url,
                    "title": title,
                    "text": text
                })
                counter += 1
                print(f"✅ [{counter}] {title}")

            time.sleep(0.25)  # freundlich crawlen
        except Exception as e:
            print(f"⚠ Fehler bei {url}: {e}")

    def collect_links(base_path):
        try:
            res = requests.get(source["base_url"] + base_path, timeout=15)
            soup = BeautifulSoup(res.text, "html.parser")
            links = [a.get("href") for a in soup.select(source["article_selector"])]
            print(f"🔍 {len(links)} Links gefunden auf {base_path}")
            return [l for l in links if l and "/" in l]
        except Exception as e:
            print(f"⚠ Fehler beim Link-Sammeln: {e}")
            return []

    if "start_paths" in source:
        for path in source["start_paths"]:
            links = collect_links(path)
            for link in links:
                scrape_page(link)
    else:
        links = collect_links(source["start_path"])
        for link in links:
            scrape_page(link)

    return articles

if __name__ == "__main__":
    print("\n▶ Starte OER-Scraping...")
    all_articles = []
    for src in OER_SOURCES:
        print(f"\n🌐 {src['name']}...")
        data = scrape_articles(src)
        all_articles.extend(data)

    with open("data/oer_texts.jsonl", "w", encoding="utf-8") as f:
        for item in all_articles:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ OER-Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → data/oer_texts.jsonl")

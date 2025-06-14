import requests
from bs4 import BeautifulSoup
import json
import time

# Konfiguration pro Quelle
OER_SOURCES = [
    {
        "name": "kindersache",
        "base_url": "https://www.kindersache.de",
        "start_paths": ["/bereiche/wissen/natur-und-mensch"],
        "article_selector": "div.view-content a",
        "content_selector": "div.field--name-body"
    },
    {
        "name": "hanisauland",
        "base_url": "https://www.hanisauland.de",
        "start_paths": [f"/wissen/lexikon/grosses-lexikon/{chr(i)}" for i in range(97, 123)],
        "article_selector": "ul.linklist__list a",
        "content_selector": "div.text"
    },
    {
        "name": "geo",
        "base_url": "https://www.geo.de",
        "start_paths": ["/geolino/tierlexikon", "/geolino/mensch"],
        "article_selector": "a.m-teaser",
        "content_selector": "div.c-article-text"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}


def scrape_articles(source):
    articles = []
    visited = set()
    counter = 0
    limit = 50

    def scrape_page(url):
        nonlocal counter
        try:
            full_url = url if url.startswith("http") else source["base_url"] + url
            if full_url in visited:
                return
            visited.add(full_url)

            res = requests.get(full_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            content = soup.select_one(source["content_selector"])
            if not content:
                return

            title = soup.title.text.strip() if soup.title else "No title"
            text = content.get_text(separator="\n").strip()

            if len(text) > 200:
                articles.append({"url": full_url, "title": title, "text": text})
                counter += 1
                print(f"✅ [{counter}] {title}")

                if counter % limit == 0:
                    print(f"🔁 {limit} Artikel gespeichert… fahre automatisch fort…")

        except Exception as e:
            print(f"⚠ Fehler bei {url}: {e}")

    def collect_links(base_path):
        try:
            url = source["base_url"] + base_path
            res = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = [a.get("href") for a in soup.select(source["article_selector"])]
            return [l for l in links if l and "/" in l]
        except Exception as e:
            print(f"⚠ Fehler beim Sammeln von Links unter {base_path}: {e}")
            return []

    if "start_paths" in source:
        for path in source["start_paths"]:
            links = collect_links(path)
            print(f"🔍 {len(links)} Links gefunden auf {path}")
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

    with open("data/oer_texts.jsonl", "w") as f:
        for item in all_articles:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ OER-Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → data/oer_texts.jsonl")


import requests
from bs4 import BeautifulSoup
import json
import time

KINDERSACHE_WISSEN_PATHS = [
    "/bereiche/wissen/politik",
    "/bereiche/wissen/andere-laender",
    "/bereiche/wissen/natur-und-mensch",
    "/bereiche/wissen/gesundheit",
    "/bereiche/wissen/sport",
    "/bereiche/wissen/panorama",
    "/bereiche/wissen/medien",
    "/bereiche/wissen/lernen",
    "/bereiche/wissen/lexikon",
    "/bereiche/wissen/journalisten-abc"
]

BASE_URL = "https://www.kindersache.de"
ARTICLE_SELECTOR = "div.view-content a"
CONTENT_SELECTOR = "div.field--name-body"
OUTPUT_FILE = "data/oer_texts.jsonl"


def get_article_links(start_path):
    print(f"🔍 Scanning {BASE_URL}{start_path}...")
    try:
        res = requests.get(BASE_URL + start_path, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a.get("href") for a in soup.select(ARTICLE_SELECTOR)]
        links = [l for l in links if l and l.startswith("/bereiche/wissen") and "/" in l]
        return links
    except Exception as e:
        print(f"⚠ Fehler beim Laden von {start_path}: {e}")
        return []


def scrape_article(url):
    full_url = BASE_URL + url if not url.startswith("http") else url
    try:
        res = requests.get(full_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one(CONTENT_SELECTOR)
        title = soup.title.text.strip() if soup.title else "No title"

        if content:
            text = content.get_text(separator="\n").strip()
            if len(text) > 200:
                return {"url": full_url, "title": title, "text": text}
    except Exception as e:
        print(f"⚠ Fehler bei Artikel {full_url}: {e}")
    return None


if __name__ == "__main__":
    print("\n▶ Starte OER-Scraping kindersache.de (alle Wissen-Rubriken)...")
    all_articles = []
    scraped = 0
    for path in KINDERSACHE_WISSEN_PATHS:
        article_links = get_article_links(path)
        print(f"➡ {len(article_links)} Links gefunden auf {path}")

        for link in article_links:
            data = scrape_article(link)
            if data:
                all_articles.append(data)
                scraped += 1
                print(f"✅ [{scraped}] {data['title']}")
                if scraped % 50 == 0:
                    print("💾 50 Artikel verarbeitet. Speichere Zwischenergebnis...")
                    with open(OUTPUT_FILE, "a") as f:
                        for article in all_articles:
                            json.dump(article, f, ensure_ascii=False)
                            f.write("\n")
                    all_articles = []
                    time.sleep(1)

    # Final speichern
    if all_articles:
        with open(OUTPUT_FILE, "a") as f:
            for article in all_articles:
                json.dump(article, f, ensure_ascii=False)
                f.write("\n")

    print(f"\n✅ OER-Scraping abgeschlossen. Artikel gespeichert → {OUTPUT_FILE}")

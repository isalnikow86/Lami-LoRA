import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.kindersache.de"
CATEGORIES = [
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
ARTICLE_SELECTOR = "div.view-content a"
CONTENT_SELECTOR = "div.field--name-body"

def collect_article_links(start_path):
    try:
        res = requests.get(BASE_URL + start_path, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a.get("href") for a in soup.select(ARTICLE_SELECTOR)]
        links = [l for l in links if l and l.startswith("/bereiche/wissen/") and "/" in l]
        print(f"➡ {len(links)} Links gefunden auf {start_path}")
        return links
    except Exception as e:
        print(f"⚠ Fehler beim Laden von {start_path}: {e}")
        return []

def scrape_article(url, content_selector):
    full_url = BASE_URL + url if not url.startswith("http") else url
    try:
        res = requests.get(full_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one(content_selector)
        title = soup.title.text.strip() if soup.title else "No title"

        if content:
            text = content.get_text(separator="\n").strip()
            if len(text) > 200:
                return {"url": full_url, "title": title, "text": text}
    except Exception as e:
        print(f"⚠ Fehler bei Artikel {full_url}: {e}")
    return None

if __name__ == "__main__":
    print("▶ Starte OER-Scraping kindersache.de (alle Wissen-Rubriken)...")
    all_articles = []

    for path in CATEGORIES:
        print(f"\n🔍 Scanning {BASE_URL + path}...")
        links = collect_article_links(path)
        for link in links:
            article = scrape_article(link, CONTENT_SELECTOR)
            if article:
                all_articles.append(article)

    with open("data/kindersache_texts.jsonl", "w") as f:
        for item in all_articles:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ OER-Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → data/kindersache_texts.jsonl")

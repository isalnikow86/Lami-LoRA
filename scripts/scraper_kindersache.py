import requests
from bs4 import BeautifulSoup
import json
import time

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
    "/bereiche/wissen/journalisten-abc",
]

ARTICLE_SELECTOR = "div.view-content a"
CONTENT_SELECTORS = [
    "div.text",                    # fallback 1
    "div.field--name-body",        # fallback 2
    "article.node-article",        # fallback 3
    "div.content",                 # fallback 4
]

def collect_links(start_path):
    print(f"\n🔍 Scanning {BASE_URL}{start_path}...")
    try:
        res = requests.get(BASE_URL + start_path, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a.get("href") for a in soup.select(ARTICLE_SELECTOR)]
        links = [l for l in links if l and "/bereiche/wissen" in l]
        print(f"➡ {len(links)} Links gefunden auf {start_path}")
        return links
    except Exception as e:
        print(f"❌ Fehler beim Laden von {start_path}: {e}")
        return []

def scrape_article(url):
    full_url = url if url.startswith("http") else BASE_URL + url
    try:
        res = requests.get(full_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = None

        for selector in CONTENT_SELECTORS:
            content = soup.select_one(selector)
            if content:
                break

        if not content:
            print(f"⚠ Kein Inhalt gefunden für Artikel {full_url}")
            return None

        text = content.get_text(separator="\n").strip()
        title = soup.title.text.strip() if soup.title else "Kein Titel"

        if len(text) > 200:
            return {"url": full_url, "title": title, "text": text}
        else:
            print(f"⚠ Artikel zu kurz: {full_url}")
    except Exception as e:
        print(f"❌ Fehler bei Artikel {full_url}: {e}")
    return None

if __name__ == "__main__":
    print("▶ Starte OER-Scraping kindersache.de (alle Wissen-Rubriken)...")
    all_articles = []

    for category in CATEGORIES:
        links = collect_links(category)
        for link in links:
            article = scrape_article(link)
            if article:
                all_articles.append(article)
            time.sleep(0.5)  # Gentle delay

    with open("data/kindersache_texts.jsonl", "w") as f:
        for a in all_articles:
            json.dump(a, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ OER-Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → data/kindersache_texts.jsonl")

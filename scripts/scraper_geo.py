import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.geo.de"
OUTPUT_FILE = "data/geo_texts.jsonl"

CATEGORIES = [
    "/geolino/tierlexikon-21334.html",
    "/geolino/redewendungen-21968.html",
    "/geolino/berufe-10151.html"
]

ARTICLE_SELECTOR = "a.o-teaser-standard__link"
CONTENT_SELECTOR = "div.c-article-text"


def get_article_links(category_url):
    try:
        res = requests.get(BASE_URL + category_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a["href"] for a in soup.select(ARTICLE_SELECTOR) if a.has_attr("href") and a["href"].startswith("/geolino/")]
        return list(set(links))
    except Exception as e:
        print(f"⚠ Fehler beim Laden von {category_url}: {e}")
        return []


def scrape_article(path):
    full_url = BASE_URL + path if path.startswith("/") else path
    try:
        res = requests.get(full_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one(CONTENT_SELECTOR)
        title = soup.title.text.strip() if soup.title else "Kein Titel"
        if content:
            text = content.get_text(separator="\n").strip()
            if len(text) > 200:
                return {"url": full_url, "title": title, "text": text}
            else:
                print(f"⚠ Artikel zu kurz: {full_url}")
        else:
            print(f"⚠ Kein Content gefunden: {full_url}")
    except Exception as e:
        print(f"⚠ Fehler bei Artikel {full_url}: {e}")
    return None


if __name__ == "__main__":
    print("\n▶ Starte GEO-Scraper...\n")
    all_articles = []

    for category in CATEGORIES:
        print(f"🔍 Scanne Bereich: {category}")
        links = get_article_links(category)
        print(f"🔗 {len(links)} Links gefunden\n")

        for link in links:
            data = scrape_article(link)
            if data:
                all_articles.append(data)
                print(f"✅ {data['title']}")
            time.sleep(0.3)

    with open(OUTPUT_FILE, "w") as f:
        for item in all_articles:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ GEO-Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → {OUTPUT_FILE}")

import requests
from bs4 import BeautifulSoup
import json
import os

OUTPUT_PATH = "data/oer_texts.jsonl"

# Hilfsfunktion zum Artikel-Scraping

def extract_article_text(url, selector):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        article = soup.select_one(selector)
        return article.get_text(strip=True, separator="\n") if article else None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Kindersache: nur Bereich Wissen

def scrape_kindersache():
    print("Scraping kindersache...")
    base = "https://www.kindersache.de"
    start_url = base + "/bereiche/wissen"
    res = requests.get(start_url)
    soup = BeautifulSoup(res.text, "html.parser")
    articles = []
    for link in soup.select("a.teaser-title"):
        href = link.get("href")
        if href and "/bereiche/wissen/" in href:
            full_url = base + href
            text = extract_article_text(full_url, "div.field--name-body")
            if text:
                articles.append({"source": full_url, "text": text})
    return articles

# HanisauLand: nur Großes Lexikon

def scrape_hanisauland():
    print("Scraping hanisauland...")
    base = "https://www.hanisauland.de"
    index_base = base + "/wissen/lexikon/grosses-lexikon"
    letters = list("abcdefghijklmnopqrstuvwxyz")
    articles = []
    for letter in letters:
        res = requests.get(f"{index_base}/{letter}/")
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.select("a.gs-text-link"):
            href = a.get("href")
            if href and href.startswith("/wissen/lexikon/grosses-lexikon/"):
                full_url = base + href
                text = extract_article_text(full_url, "div.text")
                if text:
                    articles.append({"source": full_url, "text": text})
    return articles

# GEOlino Tierlexikon und Wissen

def scrape_geolino():
    print("Scraping geo.de...")
    base = "https://www.geo.de"
    tier_url = base + "/geolino/tierlexikon"
    mensch_url = base + "/geolino/mensch"
    articles = []

    for url in [tier_url, mensch_url]:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        for link in soup.select("a.headline-link"):
            href = link.get("href")
            if href and href.startswith("/geolino"):
                full_url = base + href
                text = extract_article_text(full_url, "div.article__body")
                if text:
                    articles.append({"source": full_url, "text": text})
    return articles

# Ausführung

if __name__ == "__main__":
    print("\u270F OER Daten vorbereiten:")
    all_articles = []
    os.makedirs("data", exist_ok=True)

    all_articles.extend(scrape_kindersache())
    all_articles.extend(scrape_hanisauland())
    all_articles.extend(scrape_geolino())

    with open(OUTPUT_PATH, "w") as f:
        for entry in all_articles:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\n✅ Scraping complete. {len(all_articles)} articles saved to {OUTPUT_PATH}")

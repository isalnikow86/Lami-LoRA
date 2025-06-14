import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.hanisauland.de"
LETTERS = list("abcdefghijklmnopqrstuvwxyz")
OUTPUT_PATH = "data/oer_texts_hanisauland.jsonl"

def collect_article_links(letter):
    url = f"{BASE_URL}/wissen/lexikon/grosses-lexikon/{letter}/"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [
            a.get("href")
            for a in soup.select("div.teaser__content > a")
            if a.get("href") and "/wissen/lexikon/grosses-lexikon/" in a.get("href")
        ]
        return list(set(links))
    except Exception as e:
        print(f"⚠ Fehler bei Buchstabe {letter}: {e}")
        return []

def scrape_article(url):
    full_url = url if url.startswith("http") else BASE_URL + url
    try:
        res = requests.get(full_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.title.text.strip() if soup.title else "No title"
        content = soup.select_one("div.text")
        if content:
            text = content.get_text(separator="\n").strip()
            if len(text) > 200:
                return {"url": full_url, "title": title, "text": text}
    except Exception as e:
        print(f"⚠ Fehler beim Artikel {full_url}: {e}")
    return None

if __name__ == "__main__":
    print("▶ Starte Scraping hanisauland.de (Großes Lexikon)...")
    all_articles = []

    for letter in LETTERS:
        print(f"\n🔡 Buchstabe {letter.upper()}...", end=" ")
        links = collect_article_links(letter)
        print(f"{len(links)} Links gefunden")

        for link in links:
            article = scrape_article(link)
            if article:
                all_articles.append(article)
                print(f"✅ Artikel: {article['title']}")

    with open(OUTPUT_PATH, "w") as f:
        for item in all_articles:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ Hanisauland-Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → {OUTPUT_PATH}")

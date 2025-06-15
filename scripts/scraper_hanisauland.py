import requests
from bs4 import BeautifulSoup
import json
import time
import string

BASE_URL = "https://www.hanisauland.de"
LEXIKON_BASE = "/wissen/lexikon/grosses-lexikon/"

OUTPUT_FILE = "data/oer_texts_hanisauland.jsonl"
LETTERS = list(string.ascii_lowercase)

def get_links(letter):
    url = BASE_URL + LEXIKON_BASE + letter + "/"
    print(f"🔍 Lade {url}")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Richtiges Element für Artikel-Links
        links = [a["href"] for a in soup.select("a.dictionary-word") if a.has_attr("href")]
        print(f"🔗 {len(links)} Links gefunden")
        return links
    except Exception as e:
        print(f"⚠ Fehler beim Laden der Seite {url}: {e}")
        return []


def scrape_article(path):
    full_url = BASE_URL + path if path.startswith("/") else path
    try:
        res = requests.get(full_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one("div.text")  # Inhalt des Lexikon-Artikels
        if not content:
            print(f"⚠ Kein Content gefunden: {full_url}")
            return None

        title = soup.title.text.strip() if soup.title else "Kein Titel"
        text = content.get_text(separator="\n").strip()
        if len(text) > 200:
            return {"url": full_url, "title": title, "text": text}
        else:
            print(f"⚠ Artikel zu kurz: {full_url}")
    except Exception as e:
        print(f"⚠ Fehler bei Artikel {path}: {e}")
    return None

if __name__ == "__main__":
    print("▶ Starte Scraping hanisauland.de (Großes Lexikon)...")
    all_articles = []

    for letter in LETTERS:
        links = get_links_for_letter(letter)
        for link in links:
            article = scrape_article(link)
            if article:
                all_articles.append(article)
            time.sleep(0.3)

    with open(OUTPUT_FILE, "w") as f:
        for item in all_articles:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → {OUTPUT_FILE}")

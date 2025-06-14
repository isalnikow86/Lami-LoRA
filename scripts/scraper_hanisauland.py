import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.hanisauland.de"
OUTPUT_FILE = "data/oer_texts_hanisauland.jsonl"
LEXIKON_BASE = "/wissen/lexikon/grosses-lexikon/"

def get_links_for_letter(letter):
    url = BASE_URL + LEXIKON_BASE + letter + "/"
    print(f"\n🔡 Buchstabe {letter.upper()}... 🔍 Lade {url}")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("a.c-teaser__link")  # neuer selector!
        hrefs = [a["href"] for a in links if a.has_attr("href") and a["href"].startswith("/wissen/lexikon/grosses-lexikon/")]
        print(f"🔗 {len(hrefs)} Links gefunden")
        return hrefs
    except Exception as e:
        print(f"⚠ Fehler beim Laden von {url}: {e}")
        return []

def scrape_article(url):
    try:
        if not url.startswith("http"):
            url = BASE_URL + url

        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        content = soup.select_one("div.c-rte--article")  # korrekter Content-Block
        title = soup.title.text.strip() if soup.title else "Kein Titel"

        if content:
            text = content.get_text(separator="\n").strip()
            if len(text) > 200:
                print(f"✅ Artikel gescraped: {title}")
                return {"url": url, "title": title, "text": text}
            else:
                print(f"⚠ Artikel zu kurz: {url}")
        else:
            print(f"⚠ Kein Content gefunden: {url}")

    except Exception as e:
        print(f"⚠ Fehler bei Artikel {url}: {e}")
    return None

if __name__ == "__main__":
    print("▶ Starte Scraping hanisauland.de (Großes Lexikon)...")
    all_articles = []

    for letter in "abcdefghijklmnopqrstuvwxyz":
        links = get_links_for_letter(letter)
        for link in links:
            article = scrape_article(link)
            if article:
                all_articles.append(article)
            time.sleep(0.5)

    with open(OUTPUT_FILE, "w") as f:
        for entry in all_articles:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → {OUTPUT_FILE}")

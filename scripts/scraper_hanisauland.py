import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.hanisauland.de"
ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
ARTICLE_SELECTOR = "ul.linklist__list a"
CONTENT_SELECTOR = "div.text"

def get_links(letter):
    url = f"{BASE_URL}/wissen/lexikon/grosses-lexikon/{letter}"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a.get("href") for a in soup.select(ARTICLE_SELECTOR)]
        links = [l for l in links if l and l.startswith("/wissen/lexikon/grosses-lexikon/")]
        print(f"🔡 Buchstabe {letter.upper()} – {len(links)} Links gefunden")
        return links
    except Exception as e:
        print(f"⚠ Fehler beim Laden von {url}: {e}")
        return []

def scrape_article(url):
    full_url = BASE_URL + url
    try:
        res = requests.get(full_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one(CONTENT_SELECTOR)
        if not content:
            print(f"⚠ Kein Inhalt bei {full_url}")
            return None
        title = soup.title.text.strip() if soup.title else "Kein Titel"
        text = content.get_text(separator="\n").strip()
        if len(text) > 200:
            return {"url": full_url, "title": title, "text": text}
    except Exception as e:
        print(f"⚠ Fehler bei {full_url}: {e}")
    return None

if __name__ == "__main__":
    print("\n▶ Starte Scraping hanisauland.de (Großes Lexikon)...")
    all_articles = []

    for letter in ALPHABET:
        links = get_links(letter)
        time.sleep(1)
        for link in links:
            article = scrape_article(link)
            if article:
                all_articles.append(article)
                print(f"✅ Artikel gespeichert: {article['title']}")
            time.sleep(0.5)

    out_path = "data/oer_texts_hanisauland.jsonl"
    with open(out_path, "w") as f:
        for item in all_articles:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ Hanisauland Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → {out_path}")

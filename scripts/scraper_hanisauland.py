import requests
from bs4 import BeautifulSoup
import json
import time
import string

BASE_URL = "https://www.hanisauland.de"
LEXIKON_BASE = "/wissen/lexikon/grosses-lexikon/"
OUTPUT_FILE = "data/oer_texts_hanisauland.jsonl"

def get_links(letter):
    url = BASE_URL + LEXIKON_BASE + letter + "/"
    print(f"🔍 Lade {url}")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Debug-HTML speichern, wenn nötig
        with open(f"debug_hanisauland_{letter}.html", "w") as f:
            f.write(res.text)

        # Artikel-Links extrahieren
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(LEXIKON_BASE + letter + "/") and href.endswith(".html"):
                links.append(href)

        return list(set(links))
    except Exception as e:
        print(f"⚠ Fehler beim Laden der Seite {url}: {e}")
        return []

def scrape_article(relative_url):
    full_url = BASE_URL + relative_url
    try:
        res = requests.get(full_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one("div.textcontent")  # <-- Korrektur hier!
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
    print("▶ Starte Scraping hanisauland.de (Großes Lexikon)...\n")
    all_articles = []

    for letter in string.ascii_lowercase:
        print(f"🔡 Buchstabe {letter.upper()}...", end=" ")
        links = get_links(letter)
        print(f"{len(links)} Links gefunden")

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

    print(f"\n✅ Hanisauland Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → {OUTPUT_FILE}")

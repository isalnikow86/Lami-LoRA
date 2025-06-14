# scripts/scraper_hanisauland.py
import requests
from bs4 import BeautifulSoup
import json
import time
import string

def scrape_hanisauland():
    base_url = "https://www.hanisauland.de"
    lexikon_base = "/wissen/lexikon/grosses-lexikon/"
    articles = []
    counter = 0
    visited = set()
    letters = list(string.ascii_lowercase)

    for letter in letters:
        print(f"\n🔤 Buchstabe {letter.upper()}...")
        index_url = base_url + lexikon_base + letter
        try:
            res = requests.get(index_url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.select("ul.linklist__list a")
            print(f"🔍 {len(links)} Links gefunden auf {lexikon_base + letter}")
        except:
            continue

        for a in links:
            href = a.get("href")
            if not href or href in visited:
                continue
            visited.add(href)
            url = base_url + href
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                content = soup.select_one("div.text")
                title = soup.title.text.strip()
                text = content.get_text(separator="\n").strip() if content else ""
                if len(text) > 200:
                    articles.append({"url": url, "title": title, "text": text})
                    counter += 1
                    print(f"✅ [{counter}] {title}")
            except:
                pass

    with open("data/oer_texts_hanisauland.jsonl", "w") as f:
        for article in articles:
            json.dump(article, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ Hanisauland Scraping abgeschlossen. {counter} Artikel gespeichert → data/oer_texts_hanisauland.jsonl")

if __name__ == "__main__":
    scrape_hanisauland()

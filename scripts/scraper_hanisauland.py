import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.hanisauland.de"
ABC_PATHS = [f"/wissen/lexikon/grosses-lexikon/{chr(c)}" for c in range(ord("a"), ord("z") + 1)]

def get_article_links(path):
    try:
        res = requests.get(BASE_URL + path, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [
            a["href"] for a in soup.select("a.linklist__link")
            if a.get("href", "").startswith(path + "/")  # z. B. /wissen/lexikon/grosses-lexikon/a/abgeordnete.html
        ]
        return links
    except Exception as e:
        print(f"⚠ Fehler bei {path}: {e}")
        return []

def scrape_article(url):
    full_url = url if url.startswith("http") else BASE_URL + url
    try:
        res = requests.get(full_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one("div.text")
        title = soup.title.text.strip() if soup.title else "Kein Titel"
        if content:
            text = content.get_text(separator="\n").strip()
            if len(text) > 200:
                return {"url": full_url, "title": title, "text": text}
    except Exception as e:
        print(f"⚠ Fehler bei Artikel {full_url}: {e}")
    return None

if __name__ == "__main__":
    print("▶ Starte Scraping hanisauland.de (Großes Lexikon)...\n")
    all_articles = []

    for path in ABC_PATHS:
        print(f"🔡 Buchstabe {path[-1].upper()}...", end=" ")
        links = get_article_links(path)
        print(f"{len(links)} Links gefunden")
        for link in links:
            article = scrape_article(link)
            if article:
                all_articles.append(article)
                print(f"✅ {article['title']}")
    
    with open("data/oer_texts_hanisauland.jsonl", "w") as f:
        for item in all_articles:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")
    
    print(f"\n✅ Hanisauland Scraping abgeschlossen. {len(all_articles)} Artikel gespeichert → data/oer_texts_hanisauland.jsonl")

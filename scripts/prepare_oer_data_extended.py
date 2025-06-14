import requests
from bs4 import BeautifulSoup
import json
import time

OUTPUT_PATH = "data/oer_texts.jsonl"

# Zielbereiche definieren
TARGETS = {
    "kindersache.de": {
        "base": "https://www.kindersache.de",
        "start": "https://www.kindersache.de/bereiche/wissen/natur-und-mensch",
        "include": ["/bereiche/wissen/natur-und-mensch"],
    },
    "hanisauland.de": {
        "base": "https://www.hanisauland.de",
        "start": "https://www.hanisauland.de/wissen/lexikon/grosses-lexikon/a",
        "include": ["/wissen/lexikon/grosses-lexikon/"],
    },
    "geo.de": {
        "base": "https://www.geo.de",
        "start": "https://www.geo.de/geolino/tierlexikon",
        "include": ["/geolino/tierlexikon", "/geolino/mensch"],
    }
}

def fetch_article(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")

        # Extrahiere sichtbaren Text
        article = soup.find("article") or soup.find("main")
        if not article:
            return None
        text = article.get_text(separator="\n", strip=True)
        if len(text) < 200:
            return None
        title = soup.title.string if soup.title else ""
        return {"url": url, "title": title, "text": text}
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def collect_links(base_url, start_url, includes):
    visited = set()
    to_visit = [start_url]
    found_links = []

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)
        print(f"🔎 Scanning {url}")
        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("/") and any(inc in href for inc in includes):
                    full_url = base_url + href
                    if full_url not in visited and full_url not in to_visit:
                        to_visit.append(full_url)
                        if href.count("/") >= 4:  # primitive Artikel-Filterung
                            found_links.append(full_url)
        except Exception as e:
            print(f"Failed to scan {url}: {e}")
            continue
        time.sleep(0.5)
    return list(set(found_links))

def main():
    all_articles = []
    print("\n✏ Starte OER-Scraping...")
    for domain, config in TARGETS.items():
        print(f"\n🌐 {domain}...")
        links = collect_links(config["base"], config["start"], config["include"])
        print(f"→ {len(links)} potenzielle Artikel gefunden")
        for url in links:
            art = fetch_article(url)
            if art:
                all_articles.append(art)
            time.sleep(0.2)

    print(f"\n✅ Fertig! {len(all_articles)} Artikel gespeichert unter {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for entry in all_articles:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

if __name__ == "__main__":
    main()

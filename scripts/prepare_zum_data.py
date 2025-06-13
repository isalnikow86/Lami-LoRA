import requests
from bs4 import BeautifulSoup
import json
import time

# WICHTIG: hier alle gewünschten Kategorien eintragen
CATEGORY_URLS = [
    "https://unterrichten.zum.de/wiki/Kategorie:Geographie",
    "https://unterrichten.zum.de/wiki/Kategorie:Geschichte",
    "https://unterrichten.zum.de/wiki/Kategorie:Physik",
    "https://unterrichten.zum.de/wiki/Kategorie:Mathematik",
    "https://unterrichten.zum.de/wiki/Kategorie:Politik",
    "https://unterrichten.zum.de/wiki/Kategorie:Ethik",
    "https://unterrichten.zum.de/wiki/Kategorie:Sachartikel",
    "https://unterrichten.zum.de/wiki/Kategorie:Biografien",
]

BASE_URL = "https://unterrichten.zum.de"

# Funktion: alle Artikel-Links aus einer Kategorie holen
def get_article_links(category_url):
    print(f"📚 Scraping category: {category_url} ...")
    links = []
    next_page = category_url
    while next_page:
        res = requests.get(next_page)
        soup = BeautifulSoup(res.text, "html.parser")

        # Artikel-Links finden
        for li in soup.select(".mw-category li a"):
            link = BASE_URL + li["href"]
            links.append(link)

        # Prüfen, ob es eine "nächste Seite" gibt (bei großen Kategorien)
        next_link = soup.find("a", text="nächste Seite")
        if next_link:
            next_page = BASE_URL + next_link["href"]
        else:
            next_page = None

    print(f"✅ Found {len(links)} articles in category.")
    return links

# Funktion: Artikeltext von einer Artikel-URL extrahieren
def scrape_article(article_url):
    res = requests.get(article_url)
    soup = BeautifulSoup(res.text, "html.parser")

    # Artikel-Titel
    title = soup.select_one("#firstHeading").text.strip()

    # Artikel-Text
    paragraphs = soup.select("#mw-content-text p")
    text = "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip() != ""])

    return {"title": title, "text": text}

# Main
if __name__ == "__main__":
    all_articles = []

    for category_url in CATEGORY_URLS:
        article_links = get_article_links(category_url)

        for idx, article_url in enumerate(article_links):
            print(f"[{idx+1}/{len(article_links)}] Scraping article: {article_url}")
            try:
                article_data = scrape_article(article_url)
                # Nur Artikel speichern, die nicht leer sind
                if article_data["text"]:
                    all_articles.append(article_data)
            except Exception as e:
                print(f"⚠️ Error scraping {article_url}: {e}")

            time.sleep(1)  # etwas warten, um die Server nicht zu belasten

    # Speichern als JSONL
    output_path = "data/oer_zum_texts.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for article in all_articles:
            json.dump(article, f, ensure_ascii=False)
            f.write("\n")

    print(f"\n✅ Done! {len(all_articles)} articles saved to {output_path}")

import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://klexikon.zum.de"
CATEGORY_URLS = [
    "https://klexikon.zum.de/wiki/Kategorie:Artikel",
    "https://klexikon.zum.de/wiki/Kategorie:Sachartikel",
    "https://klexikon.zum.de/wiki/Kategorie:Biografien"
]

def get_article_links():
    print("Fetching article links from categories...")
    links = []

    for category_url in CATEGORY_URLS:
        print(f"Processing category: {category_url}")
        next_page = category_url

        while next_page:
            r = requests.get(next_page)
            soup = BeautifulSoup(r.text, "html.parser")
            page_links = [
                BASE_URL + a["href"]
                for a in soup.select("div#mw-pages li a")
                if a["href"].startswith("/wiki/")
            ]
            links.extend(page_links)

            # Find "nächste Seite" link if available
            nav_links = soup.select("div#mw-pages a")
            next_page = None
            for link in nav_links:
                if "nächste seite" in link.text.lower():
                    next_page = BASE_URL + link["href"]
                    print(f"Found next page: {next_page}")
                    break

            time.sleep(0.5)  # polite crawling

    return list(set(links))  # remove duplicates

def scrape_article(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("h1").text.strip()
    paragraphs = soup.select("div.mw-parser-output > p")
    text = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
    return {"title": title, "text": text}

def main():
    links = get_article_links()
    print(f"Found {len(links)} articles.")
    with open("data/klexikon_texts.jsonl", "w", encoding="utf-8") as f:
        for i, link in enumerate(links, 1):
            article = scrape_article(link)
            json.dump(article, f, ensure_ascii=False)
            f.write("\n")
            print(f"[{i}/{len(links)}] Saved: {article['title']}")

if __name__ == "__main__":
    main()

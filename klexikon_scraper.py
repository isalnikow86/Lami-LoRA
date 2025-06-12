import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://klexikon.zum.de"

SITEMAP_URL = "https://klexikon.zum.de/wiki/Spezial:Alle_Seiten"

def get_article_links():
    print("Fetching article links from sitemap...")
    links = []
    next_page = SITEMAP_URL

    while next_page:
        print(f"Processing page: {next_page}")
        r = requests.get(next_page)
        soup = BeautifulSoup(r.text, "html.parser")
        page_links = [
            BASE_URL + a["href"]
            for a in soup.select("div.mw-allpages-body ul li a")
            if a["href"].startswith("/wiki/")
        ]
        links.extend(page_links)

        # Check for next page link
        next_link = soup.select_one("div.mw-allpages-nav a[title='Spezial:Alle Seiten']")
        if next_link and "weiter" in next_link.text.lower():
            next_page = BASE_URL + next_link["href"]
            time.sleep(0.5)  # polite crawling
        else:
            next_page = None

    return links

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

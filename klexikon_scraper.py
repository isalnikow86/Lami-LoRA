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

        # Find the "weiter" link in navigation
        nav_links = soup.select("div.mw-allpages-nav a")
        next_page = None
        for link in nav_links:
            if "weiter" in link.text.lower():
                next_page = BASE_URL + link["href"]
                break

        # polite crawling → avoid hammering the server
        time.sleep(0.5)

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

import os
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Zielverzeichnis für gesammelte Artikel
output_path = "data/oer_texts.jsonl"
os.makedirs("data", exist_ok=True)

articles = []

def save_articles():
    with open(output_path, "w", encoding="utf-8") as f:
        for article in articles:
            f.write(json.dumps(article, ensure_ascii=False) + "\n")
    print(f"\n✅ Scraping complete. {len(articles)} articles saved to {output_path}")

def scrape_kindersache():
    print("Scraping kindersache...")
    base_url = "https://www.kindersache.de"
    start_url = base_url + "/bereiche/wissen"
    res = requests.get(start_url)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select(".view-content a")
    visited = set()

    for link in links:
        href = link.get("href")
        if href and "/bereiche/wissen/" in href and href not in visited:
            visited.add(href)
            url = urljoin(base_url, href)
            try:
                page = requests.get(url)
                page_soup = BeautifulSoup(page.text, "html.parser")
                title = page_soup.find("h1").text.strip()
                body = page_soup.find("div", class_="field--name-body")
                if body:
                    text = body.get_text(" ", strip=True)
                    articles.append({"source": "kindersache", "title": title, "url": url, "text": text})
            except Exception as e:
                print(f"❌ Error scraping {url}: {e}")
            time.sleep(0.5)

def scrape_hanisauland():
    print("Scraping hanisauland...")
    base_url = "https://www.hanisauland.de"
    lexikon_base = base_url + "/wissen/lexikon/grosses-lexikon"

    for letter in "abcdefghijklmnopqrstuvwxyz":
        url = f"{lexikon_base}/{letter}/"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("a.teaser")

        for link in links:
            href = link.get("href")
            full_url = urljoin(base_url, href)
            try:
                page = requests.get(full_url)
                page_soup = BeautifulSoup(page.text, "html.parser")
                title = page_soup.find("h1").text.strip()
                body = page_soup.find("div", class_="article-text")
                if body:
                    text = body.get_text(" ", strip=True)
                    articles.append({"source": "hanisauland", "title": title, "url": full_url, "text": text})
            except Exception as e:
                print(f"❌ Error scraping {full_url}: {e}")
            time.sleep(0.5)

def scrape_geolino():
    print("Scraping geo.de...")
    base_url = "https://www.geo.de"
    sections = [
        "/geolino/tierlexikon/",
        "/geolino/mensch/",
        "/geolino/natur/",
    ]
    for section in sections:
        for i in range(1, 6):  # nur erste Seiten durchgehen
            url = base_url + section + f"?page={i}"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.select("a.card-teaser")

            for link in links:
                href = link.get("href")
                full_url = urljoin(base_url, href)
                try:
                    page = requests.get(full_url)
                    page_soup = BeautifulSoup(page.text, "html.parser")
                    title = page_soup.find("h1").text.strip()
                    body = page_soup.find("div", class_="article-body")
                    if body:
                        text = body.get_text(" ", strip=True)
                        articles.append({"source": "geolino", "title": title, "url": full_url, "text": text})
                except Exception as e:
                    print(f"❌ Error scraping {full_url}: {e}")
                time.sleep(0.5)

if __name__ == "__main__":
    print("✏ OER Daten vorbereiten:")
    scrape_kindersache()
    scrape_hanisauland()
    scrape_geolino()
    save_articles()

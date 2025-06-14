import requests
from bs4 import BeautifulSoup
import json
import os

# Zielverzeichnis
os.makedirs("data", exist_ok=True)
output_path = "data/oer_texts.jsonl"

articles = []

# 1. Kindersache.de (https://www.kindersache.de/bereiche/wissen)
def scrape_kindersache():
    base_url = "https://www.kindersache.de"
    start_url = base_url + "/bereiche/wissen"
    res = requests.get(start_url)
    soup = BeautifulSoup(res.text, "html.parser")
    links = [a["href"] for a in soup.select("a.teaser") if a["href"].startswith("/")]
    for link in links:
        url = base_url + link
        try:
            r = requests.get(url)
            s = BeautifulSoup(r.text, "html.parser")
            title = s.find("h1").text.strip()
            content = "\n".join(p.text.strip() for p in s.select(".text-content p"))
            if content:
                articles.append({"source": "kindersache", "title": title, "content": content})
        except Exception as e:
            print(f"Error scraping {url}: {e}")

# 2. Hanisauland.de

def scrape_hanisauland():
    base_url = "https://www.hanisauland.de"
    start_url = base_url + "/wissen/lexikon"
    res = requests.get(start_url)
    soup = BeautifulSoup(res.text, "html.parser")
    links = [a["href"] for a in soup.select("a.c-teaser") if a["href"].startswith("/wissen/lexikon/")]
    for link in links:
        url = base_url + link
        try:
            r = requests.get(url)
            s = BeautifulSoup(r.text, "html.parser")
            title = s.find("h1").text.strip()
            content = "\n".join(p.text.strip() for p in s.select(".o-article-text p"))
            if content:
                articles.append({"source": "hanisauland", "title": title, "content": content})
        except Exception as e:
            print(f"Error scraping {url}: {e}")

# 3. FragFinn.de – keine kindgerechten Inhalte mehr auffindbar, daher auslassen

# 4. Geolino.de – Zugriffsbeschränkungen, daher auslassen (außer wir nutzen Geolocation + Consent-Automation)

# 5. Kindernetz FAQ (Artikel einzeln sammeln)
def scrape_kindernetz():
    url = "https://www.kindernetz.de/wissen/frage-trifft-antwort-100.html"
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a["href"] for a in soup.select("a.teaser") if a["href"].startswith("/")]
        for link in links:
            full_url = "https://www.kindernetz.de" + link
            try:
                r = requests.get(full_url)
                s = BeautifulSoup(r.text, "html.parser")
                title = s.find("h1").text.strip()
                content = "\n".join(p.text.strip() for p in s.select(".text-content p"))
                if content:
                    articles.append({"source": "kindernetz", "title": title, "content": content})
            except Exception as e:
                print(f"Error scraping {full_url}: {e}")
    except Exception as e:
        print(f"Error loading Kindernetz index page: {e}")

# Ausführen:
print("Scraping kindersache...")
scrape_kindersache()
print("Scraping hanisauland...")
scrape_hanisauland()
print("Scraping kindernetz...")
scrape_kindernetz()

# Speichern
with open(output_path, "w") as f:
    for a in articles:
        json.dump(a, f, ensure_ascii=False)
        f.write("\n")

print(f"\n✅ Scraping complete. {len(articles)} articles saved to {output_path}")

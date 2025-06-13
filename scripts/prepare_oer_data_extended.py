import requests
from bs4 import BeautifulSoup
import json
import time

OER_URLS = [
    "https://www.kindersache.de/bereiche/wissen/",
    "https://www.hanisauland.de/wissen/lexikon/",
    "https://www.planet-schule.de/sf/themenseite.php?seite=kindernetz",  # Beispiel, muss evtl. angepasst werden
    "https://www.fragfinn.de/",
    "https://www.geo.de/geolino/",
    "https://www.kindernetz.de/wissen/frage-trifft-antwort-102.html",
]

def scrape_url(url):
    print(f"Scraping {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Default fallback: get all <p> texts
        paragraphs = soup.find_all("p")
        text = "\n\n".join([p.get_text(strip=True) for p in paragraphs])

        # site-specific tweaks → here you can add more later:
        if "kindersache.de" in url:
            content = soup.find("div", {"class": "field--name-body"})
            if content:
                text = content.get_text(strip=True)

        elif "hanisauland.de" in url:
            content = soup.find("div", {"class": "field--name-field-article-text"})
            if content:
                text = content.get_text(strip=True)

        elif "geo.de" in url:
            content = soup.find("article")
            if content:
                text = content.get_text(strip=True)

        return text

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

# Main:
if __name__ == "__main__":
    texts = []

    for url in OER_URLS:
        text = scrape_url(url)
        if text.strip():
            texts.append({"source": url, "text": text})
        time.sleep(1)  # polite crawling

    # Save to JSONL
    output_path = "data/oer_texts.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for item in texts:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

    print(f"✅ Scraping complete. {len(texts)} articles saved to {output_path}")

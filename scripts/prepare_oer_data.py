import requests
from bs4 import BeautifulSoup
import json

# Beispielquelle: ZUM.de OER Bereich (kannst du später erweitern)
OER_URLS = [
    "https://www.zum.de/wiki/ZUM-Kinderlexikon",  # als Beispiel
    # Hier später weitere OER Quellen ergänzen
]

def scrape_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Sehr simples Beispiel: alle Absätze <p>
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text() for p in paragraphs])
        
        return text.strip()
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def main():
    output_file = "data/oer_texts.jsonl"
    count = 0

    with open(output_file, "w", encoding="utf-8") as f:
        for url in OER_URLS:
            print(f"Scraping {url}...")
            text = scrape_text_from_url(url)
            
            if text:
                json.dump({"text": text}, f, ensure_ascii=False)
                f.write("\n")
                count += 1
    
    print(f"\n✅ Scraping complete. {count} articles saved to {output_file}")

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import json

# Beispielquelle: ZUM.de OER Bereich (kannst du später erweitern)
OER_URLS = [
    # ZUM-Kinderlexikon → Startseite
    "https://www.zum.de/wiki/ZUM-Kinderlexikon",
    
    # Beispielthemen im ZUM-Kinderlexikon → gut scrapen:
    "https://www.zum.de/wiki/Kategorie:Klexikon-Artikel",
    "https://www.zum.de/wiki/Kategorie:Sachartikel",
    "https://www.zum.de/wiki/Kategorie:Biografien",
    
    # WirLernenOnline.de → OER für Grundschule:
    "https://wirlernenonline.de/lernen/kinderwissen/natur-und-umwelt/",
    "https://wirlernenonline.de/lernen/kinderwissen/tiere/",
    "https://wirlernenonline.de/lernen/kinderwissen/technik/",
    "https://wirlernenonline.de/lernen/kinderwissen/geschichte/",
    "https://wirlernenonline.de/lernen/kinderwissen/erde-und-weltall/",
    
    # Kindersache.de (OER / CC Inhalte → explizit erlaubt):
    "https://www.kindersache.de/bereiche/wissen",
    
    # Hanisauland.de (OER / kindgerechte Politik):
    "https://www.hanisauland.de/wissen/lexikon",
    
    # Planet Schule → kindgerechte Inhalte (viel CC):
    "https://www.planet-schule.de/sf/filme-online.php",  # hier musst du dann **Textseiten raussuchen**, keine Videos
    
    # FragFinn.de → kindgerechte Fragen und Antworten:
    "https://www.fragfinn.de/",
    
    # Geolino (CC Inhalte → viele Artikel frei nutzbar):
    "https://www.geo.de/geolino",
    
    # Kinder-FAQ vom SWR Kindernetz:
    "https://www.kindernetz.de/wissen/frage-trifft-antwort-102.html",
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

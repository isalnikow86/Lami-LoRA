import requests from bs4 import BeautifulSoup import json BASE_URL = "https://klexikon.zum.de/wiki/" ARTICLE_LIST_URL = 
"https://klexikon.zum.de/wiki/Kategorie:Artikel" def get_article_links():
    r = requests.get(ARTICLE_LIST_URL) soup = BeautifulSoup(r.text, "html.parser") links = [ "https://klexikon.zum.de" + a["href"] for a in 
        soup.select("div#mw-pages a") if a["href"].startswith("/wiki/")
    ] return links def scrape_article(url): r = requests.get(url) soup = BeautifulSoup(r.text, "html.parser") title = 
    soup.find("h1").text.strip() paragraphs = soup.select("div.mw-parser-output > p") text = "\n".join([p.text.strip() for p in paragraphs 
    if p.text.strip()]) return {"title": title, "text": text}
def main(): links = get_article_links() print(f"Found {len(links)} articles.") with open("data/klexikon_texts.jsonl", "w", 
    encoding="utf-8") as f:
        for link in links: article = scrape_article(link) json.dump(article, f, ensure_ascii=False) f.write("\n") print(f"Saved: 
            {article['title']}")
if __name__ == "__main__":
    main()

def scrape_article(url):
    try:
        if not url.startswith("http"):
            url = BASE_URL + url

        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        content = soup.select_one("div.c-rte--article")  # korrekter Content-Container
        title = soup.title.text.strip() if soup.title else "No title"

        if content:
            text = content.get_text(separator="\n").strip()
            if len(text) > 200:
                return {"url": url, "title": title, "text": text}
            else:
                print(f"⚠ Artikel zu kurz: {url}")
        else:
            print(f"⚠ Kein Content gefunden: {url}")

    except Exception as e:
        print(f"⚠ Fehler bei Artikel {url}: {e}")
    return None

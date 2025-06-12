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

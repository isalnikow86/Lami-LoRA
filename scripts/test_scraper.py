
import requests
from bs4 import BeautifulSoup

url = "https://www.kindersache.de/bereiche/wissen/natur-und-mensch"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

for a in soup.find_all("a", href=True):
    print(a["href"])

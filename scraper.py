from bs4 import BeautifulSoup
import requests
import utils


url = "http://www.gsmarena.com/xiaomi_redmi_note_2-6992.php"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
}


r = requests.get(url, headers=utils.merge(DEFAULT_HEADERS, {}))
soup = BeautifulSoup(r.text)


for t in soup.select('table'):
    section = t.select('th')[0].contents[0]
    h = [e.contents[0] for e in t.select('.ttl > a')]
    c = [e.contents[0] for e in t.select('.nfo')]
    print dict(zip(h, c))

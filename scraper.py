import sys
import socks
import socket
from bs4 import BeautifulSoup
import requests
import utils
import csv

reload(sys)
sys.setdefaultencoding("utf8")

socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5,
        addr='127.0.0.1', port=9050)

socket.socket = socks.socksocket


with open('filtered_urls.csv', 'rb') as f:
    rows = csv.reader(f)
    urls = [r[0] for r in rows]
    urls = urls[1:]

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
}

with open('sample.csv', 'w') as csvfile:
    fieldnames = ['Model', 'GPRS', '2G bands', 'Speed', '3G bands', 'EDGE',
            'Technology', 'Status', 'SIM', '4G bands', 'Announced', 
            'Dimensions', 'Weight', 'Resolution', 'Multitouch', 'Type', 'Size',
            'Chipset', 'OS', 'CPU', 'GPU', 'Internal', 'Card slot', 
            'Secondary', 'Video', 'Primary', 'Features', 'Loudspeaker', 
            '3.5mm jack', 'Alert types', 'WLAN', 'USB', 'Infrared port', 
            'Bluetooth', 'Radio', 'GPS', 'Messaging', 'Sensors', 'Java', 
            'Browser', 'Talk time', 'Stand-by', 'Music play', 'Price group', 
            'Colors', 'Battery life', 'Camera', 'Audio quality', 'Performance', 
            'Display', 'Phonebook', 'Call records', 'Games', 'SAR EU', 
            'SAR US', 'Protection', 'Keyboard', 'NFC', 'Build', 'Alarm', 
            'Clock', 'Languages']
    writer = csv.DictWriter(
        csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for u in urls:
        print 'url', u
        r = requests.get(u, headers=utils.merge(DEFAULT_HEADERS, {}))
        print 'r.text'
        print r.text
        soup = BeautifulSoup(r.text, 'lxml')
        data = {}
        for t in soup.select('table'):
            h = []
            for e in t.select('.ttl > a'):
                h.append(e.contents[0])
            c=[]
            for e in t.select('.nfo'):
                if e.contents:
                    c.append(e.contents[0])
            section = t.select('th')[0].contents[0]
            #h = [e.contents[0] for e in t.select('.ttl > a')]
            #c = [str(e.contents[0]).encode('utf-8') for e in t.select('.nfo')]
            data.update(dict(zip(h, c)))
        title = soup.select('.specs-phone-name-title')[0].get_text()
        data.update({'Model': title})
        if 'Technology' in data:
            data['Technology'] = str(data['Technology']).strip('<a class="link-network-detail collapse" href="#"></a>')
        print data
        writer.writerow(data)

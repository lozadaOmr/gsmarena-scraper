import argparse
import sys
import socks
import socket
from bs4 import BeautifulSoup
import requests
import utils
import csv
from google import search

reload(sys)
sys.setdefaultencoding("utf8")

# [TODO] put another scraper type
# Get parser type using argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-t', '--type',
                    default='urls',
                    choices=['urls', 'models'],
                    help="""
Type:
    1. urls (default) - checks filtered_urls.csv for links. Should be a valid
        gsmarena link. Format: link
    2. model - checks filtered_models.csv for manufacturer + model. Searches
        model to google to return valid gsmarena link.
        Format: manufacturer,model
                    """.strip())

args = parser.parse_args()

if args.type == 'models':
    with open('filtered_urls.csv', 'wb') as fw:
        writer = csv.DictWriter(fw, fieldnames=['link'],
                                quoting=csv.QUOTE_ALL)
        writer.writeheader()

        with open('filtered_models.csv', 'rb') as fp:
            rows = csv.DictReader(fp)
            for row in rows:
                manufacturer = row['manufacturer'].lower()
                model = row['model'].lower()

                # form keyword
                keyword = "gsmarena %s %s" % (manufacturer, model)

                # google returns an iterator
                query = search(keyword, num=1, stop=1)

                print "google search: %s" % keyword

                try:
                    for url in query:
                        if ("www.gsmarena.com/%s" % manufacturer) in url:
                            writer.writerow({'link': url})
                        break
                except Exception, e:
                    print "warning:", e

# always do this
with open('filtered_urls.csv', 'rb') as f:
    rows = csv.reader(f)
    urls = [r[0] for r in rows]
    urls = urls[1:]

socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5,
        addr='127.0.0.1', port=9050)

socket.socket = socks.socksocket

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
        try:
            title = soup.select('.specs-phone-name-title')[0].get_text()
        except Exception, e:
            print "warning: possible wrong link"
            title = u
        data.update({'Model': title})
        if 'Technology' in data:
            data['Technology'] = str(data['Technology']).strip('<a class="link-network-detail collapse" href="#"></a>')
        print data
        writer.writerow(data)

from bs4 import BeautifulSoup
import requests
import utils
import json
import csv
from pprint import pprint
from collections import OrderedDict


#url = "http://www.gsmarena.com/xiaomi_redmi_note_2-6992.php"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
}


with open('GSMA_DATA_20151021.csv', 'rb') as f:
    reader = csv.DictReader(f)
    urls = {(row['gsmarena.com_link'], row['Manufacturer'], row['Model'], row['TAC']) for row in reader}


def get_contents(contents):

    if len(contents) == 0:
        return ""

    return contents[0]


def get_data(d):
    return OrderedDict({
        "2G": d.get("Network:2G bands", "N"),
        "3G": d.get("Network:3G bands", "N"),
        "4G": d.get("Network:4G bands", "N"),
        "Bluetooth": d.get("Comms:Bluetooth", "N"),
        "NFC": d.get("Comms:NFC", "N"),
        "GPS": d.get("Comms:GPS", "N"),
        "WLAN": d.get("Comms:WLAN", "N"),
        "OS": d.get("Platform:OS", "N"),
        "Multitouch": d.get("Display:Multitouch", "N"),
        "Resolution": d.get("Display:Resolution", "N"),
    })


def parse_data(url):
    r = requests.get(url, headers=utils.merge(DEFAULT_HEADERS, {}))
    soup = BeautifulSoup(r.text, "html.parser")

    if r.status_code != 200:
        return None

    full_data = {}
    for t in soup.select('table'):
        section = t.select('th')[0].contents[0]
        h = [get_contents(e.contents) for e in t.select('.ttl > a')]
        c = [get_contents(e.contents) for e in t.select('.nfo')]
        full_data[section] = dict(zip(h, c))

    new_data = {}
    for key, val in full_data.items():
        for subk, subv in val.items():
            new_data["%s:%s" % (key, subk)] = subv
            #print json.dumps({"%s:%s" % (key, subk): subv})

    return new_data


printed_headers = False
keys = []


for url, manufacturer, model, tac in urls:
    if not url:
        continue

    data = parse_data(url)
    parsed_d = get_data(data)

    if not printed_headers:
        print 'tac,manufacturer,model,' + ','.join(parsed_d.keys())
        printed_headers = True

    print ','.join(['"%s","%s","%s","%s"' % (tac, manufacturer, model, k) for k in parsed_d.values()])

import argparse
import csv
import re
import requests
import sys
import socks
import socket
import utils

from bs4 import BeautifulSoup
from google import search
from json import dumps, loads, JSONEncoder, JSONDecoder
from sqlalchemy import create_engine, Column, Integer, String, Text, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib import quote


reload(sys)
sys.setdefaultencoding("utf8")

socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5,
        addr='127.0.0.1', port=9050)

socket.socket = socks.socksocket

# [TODO] put another scraper type
# Get parser type using argparse
parser = argparse.ArgumentParser(description='Scrapes data from gsmarena.com')
parser.add_argument('-u', '--username',
                    default='root',
                    help="DB Username")
parser.add_argument('-w', '--password',
                    default='root',
                    help="DB Password")
parser.add_argument('-H', '--host',
                    default='localhost',
                    help="DB Host")
parser.add_argument('-P', '--port',
                    default=3306,
                    help="DB Port")
parser.add_argument('-d', '--database',
                    default='test',
                    help="DB Name")
parser.add_argument('-s', '--start',
                    default=1,
                    type=int,
                    help="DB start index")
parser.add_argument('-t', '--stop',
                    default=-1,
                    type=int,
                    help="DB stop index")

args = parser.parse_args()

# mysql engine url
engine_url = "mysql://%s:%s@%s:%s/%s" % (
    args.username,
    args.password,
    args.host,
    args.port,
    args.database)
engine = create_engine(engine_url)

# create session
Session = sessionmaker(bind=engine)
session = Session()

# create tables
Base = declarative_base()

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tac = Column(String(255))
    manufacturer = Column(String(255))
    model = Column(String(255))
    meta = Column(Text)
    url = Column(String(255))

Base.metadata.create_all(engine)

# process start and stop index
start_idx = args.start

if start_idx < 1:
    start_idx = 1

stop_idx = args.stop

if stop_idx < 0:
    stop_idx = session.query(Device).count()

# fill all items without url
query = session.query(Device).filter(
    and_(Device.id >= start_idx,
            Device.id <= stop_idx,
            Device.url.is_(None)))

for item in query.all():
    manufacturer = item.manufacturer.lower()
    model = item.model.lower()

    # form keyword
    keyword = "gsmarena %s %s" % (manufacturer, model)

    # use bing to search for results
    url = "http://www.bing.com/search?q={0}&go=Submit&qs=n&form=QBRE&pq={0}&sc=8-25&sp=-1&sk=&cvid=505D5E8D48744189BB96C5EC6FB91FB2".format(quote(keyword))

    print "bing search: %s" % keyword

    # get response
    response = requests.get(url)

    if response.status_code != 200:
        print "warning:", response.content
        continue

    # match format
    master = "http://www.gsmarena.com/%s" % manufacturer
    content = response.content
    preg = 'href="%s(.*?)"' % master

    match = re.search(preg, content)

    if match:
        item.url = "%s%s" % (master, match.groups()[0])
    else:
        item.url = "n/a"
    session.commit()

    # # google returns an iterator
    # query = search(keyword, num=1, stop=1)

    # print "google search: %s" % keyword

    # try:
    #     for url in query:
    #         if ("www.gsmarena.com/%s" % master) in url:
    #             item.url = url
    #         else:
    #             item.url = "n/a"
    #         session.commit()
    #         break
    # except Exception, e:
    #     print "warning:", e

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
}

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

# json serialize class
class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        return {'_python_object': str(obj)}

query = session.query(Device).filter(
    and_(Device.id >= start_idx,
            Device.id <= stop_idx,
            Device.url != "n/a",
            Device.url.isnot(None),
            Device.meta.is_(None)))

for item in query.all():
    u = item.url
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
        # section = t.select('th')[0].contents[0]
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

    item.meta = dumps(data, cls=PythonObjectEncoder)
    session.commit()

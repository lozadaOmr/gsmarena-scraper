import argparse
import csv

from json import dumps, loads, JSONEncoder, JSONDecoder
from sqlalchemy import create_engine, Column, Integer, String, Text, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


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
    manufacturer = Column(String(255))
    model = Column(String(255))
    meta = Column(Text)
    url = Column(String(255))

Base.metadata.create_all(engine)

# set csv fieldnames
fieldnames = ['manufacturer', 'model', 'wap', 'messaging', 'gprs', 'edge',
    '2g', '3g', '4g', 'wifi', 'bluetooth', 'gps', 'display_type',
    'display_size', 'camera', 'secondary_camera', 'video', 'dimensions',
    'weight', 'memory_card', 'infrared', 'usb', 'cpu', 'java']

with open("results_%s.csv" % args.database, 'wb') as fp:
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()

    query = session.query(Device).filter()

    for item in query.all():
        meta = loads(item.meta) if item.meta else {}

        if not item.url or item.url == "n/a":
            data = {
                'manufacturer': item.manufacturer,
                'model': item.model,
            }
        else:
            data = {
                'manufacturer': item.manufacturer,
                'model': item.model,
                'wap': '',
                'messaging': 1 if meta.get('Messaging') else 0,
                'gprs': 1 if meta.get('GPRS') else 0,
                'edge': 1 if meta.get('EDGE') else 0,
                '2g': 1 if meta.get('2G bands') else 0,
                '3g': 1 if meta.get('3G bands') else 0,
                '4g': 1 if meta.get('4G bands') else 0,
                'wifi':  1 if meta.get('WLAN') else 0,
                'bluetooth': 1 if meta.get('Bluetooth') else 0,
                'gps': 1 if meta.get('GPS') else 0,
                'display_type':  meta.get('Display'),
                'display_size': meta.get('Resolution'),
                'camera': meta.get('Camera'),
                'secondary_camera': '',
                'video': meta.get('Video'),
                'dimensions': meta.get('Dimensions'),
                'weight': meta.get('Weight'),
                'memory_card': meta.get('Card slot'),
                'infrared': meta.get('Infrared port'),
                'usb': 1 if meta.get('USB') else 0,
                'cpu': meta.get('CPU'),
                'java': '',
            }
        writer.writerow(data)

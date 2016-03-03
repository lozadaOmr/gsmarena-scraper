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
    tac = Column(String(255))
    manufacturer = Column(String(255))
    model = Column(String(255))
    meta = Column(Text)
    url = Column(String(255))

Base.metadata.create_all(engine)

# set csv fieldnames
fieldnames = ['tac', 'manufacturer', 'model', 'wap', 'messaging', 'gprs',
    'edge', '2g', '3g', '4g', 'wifi', 'bluetooth', 'gps', 'display_type',
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
                'tac': item.tac,
                'manufacturer': item.manufacturer,
                'model': item.model,
            }
        else:
            data = {
                'tac': item.tac,
                'manufacturer': item.manufacturer,
                'model': item.model,
                'wap': meta.get('Browser'),
                'messaging': meta.get('Messaging'),
                'gprs': meta.get('GPRS'),
                'edge': meta.get('EDGE'),
                '2g': meta.get('2G bands'),
                '3g': meta.get('3G bands'),
                '4g': meta.get('4G bands'),
                'wifi':  meta.get('WLAN'),
                'bluetooth': meta.get('Bluetooth'),
                'gps': meta.get('GPS'),
                'display_type':  meta.get('Type'),
                'display_size': meta.get('Size'),
                'camera': meta.get('Primary'),
                'secondary_camera': meta.get('Secondary'),
                'video': meta.get('Video'),
                'dimensions': meta.get('Dimensions'),
                'weight': meta.get('Weight'),
                'memory_card': meta.get('Card slot'),
                'infrared': meta.get('Infrared port'),
                'usb': meta.get('USB'),
                'cpu': meta.get('CPU'),
                'java': meta.get('Java'),
            }
        writer.writerow(data)

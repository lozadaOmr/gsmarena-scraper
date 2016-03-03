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

with open("inputs_%s.csv" % args.database, 'rb') as fp:
    reader = csv.DictReader(fp)

    for row in reader:
        item = Device(tac=row['tac'],
                      manufacturer=row['manufacturer'],
                      model=row['model'])
        session.add(item)
        session.commit()

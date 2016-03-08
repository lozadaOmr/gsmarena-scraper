#!/usr/bin/env python
# usage: scrape.py [-h] [--scheme SCHEME] [-u USERNAME] [-w PASSWORD] [-H HOST]
#                 [-P PORT] [-d DATABASE] [-s START] [-t STOP]

# Scrapes data for Novo

# optional arguments:
#   -h, --help            show this help message and exit
#   --scheme SCHEME       Database scheme
#   -u USERNAME, --username USERNAME
#                         Database username
#   -w PASSWORD, --password PASSWORD
#                         Database password
#   -H HOST, --host HOST  Database host
#   -P PORT, --port PORT  Database port
#   -d DATABASE, --database DATABASE
#                         Database name
#   -s START, --start START
#                         Database start index
#   -t STOP, --stop STOP  Database stop index

import argparse
import sys
import socks
import socket
import utils

from sqlalchemy import create_engine, Column, Integer, String, Text, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from db import DbEngine, Base, Device
from managers.urls import url_manager
from managers.scrapers import scraper_manager


# Setup proxy type
reload(sys)
sys.setdefaultencoding("utf8")

socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5,
        addr='127.0.0.1', port=9050)

socket.socket = socks.socksocket

# [TODO] put another scraper type
# Get parser type using argparse
parser = argparse.ArgumentParser(description='Scrapes data for Novo')
parser.add_argument('--scheme',
                    default='mysql',
                    help="Database scheme")
parser.add_argument('-u', '--username',
                    default='root',
                    help="Database username")
parser.add_argument('-w', '--password',
                    default='root',
                    help="Database password")
parser.add_argument('-H', '--host',
                    default='localhost',
                    help="Database host")
parser.add_argument('-P', '--port',
                    default=3306,
                    help="Database port")
parser.add_argument('-d', '--database',
                    default='test',
                    help="Database name")
parser.add_argument('-s', '--start',
                    default=1,
                    type=int,
                    help="Database start index")
parser.add_argument('-t', '--stop',
                    default=-1,
                    type=int,
                    help="Database stop index")

args = parser.parse_args()

# create engine
db_engine = DbEngine(args)
session = db_engine.session

# create all data tables
Base.metadata.create_all(db_engine.engine)

# process start and stop index
start_idx = args.start

if start_idx < 1:
    start_idx = 1

stop_idx = args.stop

if stop_idx < 0:
    stop_idx = session.query(Device).count()

if __name__ == "__main__":
    # fill all items without url
    query = session.query(Device).filter(
        and_(Device.id >= start_idx,
                Device.id <= stop_idx,
                Device.meta.is_(None)))

    for item in query.all():
        manufacturer = item.manufacturer.lower()
        model = item.model.lower()

        url = url_manager.get_url("%s %s" % (
            item.manufacturer.lower(),
            item.model.lower(),
        ))

        if url:
            item.url = url
            session.commit()

    # retrieve the data
    query = session.query(Device).filter(
        and_(Device.id >= start_idx,
                Device.id <= stop_idx,
                Device.url.isnot(None),
                Device.meta.is_(None)))

    for item in query.all():
        meta = scraper_manager.get_scraped_data(item.url)

        if meta:
            item.meta = dumps(meta, cls=utils.PythonObjectEncoder)
            session.commit()

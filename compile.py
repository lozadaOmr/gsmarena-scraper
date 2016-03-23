#!/usr/bin/env python
# usage: compile.py [-h] [--scheme SCHEME] [-u USERNAME] [-w PASSWORD] [-H HOST]
#                   [-P PORT] [-d DATABASE]

# Compiles data for Novo

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

import argparse
import unicodecsv as csv

from json import loads

from db import DbEngine, Base, Device
from managers.const import DEFAULT_FIELDNAMES
from managers.cleaners import cleaner_manager


# [TODO] put another scraper type
# Get parser type using argparse
parser = argparse.ArgumentParser(description='Compiles data for Novo')
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

args = parser.parse_args()

# create engine
db_engine = DbEngine(args)
session = db_engine.session

# create all data tables
Base.metadata.create_all(db_engine.engine)

# set csv fieldnames
fieldnames = ['tac', 'manufacturer', 'model'] + DEFAULT_FIELDNAMES

if __name__ == "__main__":
    # write to file
    with open("results/%s.csv" % args.database, 'wb') as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()

        query = session.query(Device).filter()

        for item in query.all():

            data = {
                'tac': item.tac,
                'manufacturer': item.manufacturer,
                'model': item.model,
            }

            if item.url and item.meta:
                meta = cleaner_manager.clean(item.url, loads(item.meta))
                data.update(meta)

            try:
                writer.writerow(data)
            except:
                continue

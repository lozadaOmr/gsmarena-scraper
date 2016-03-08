#!/usr/bin/env python
# usage: insert.py [-h] [--scheme SCHEME] [-u USERNAME] [-w PASSWORD] [-H HOST]
#                   [-P PORT] [-d DATABASE]

# Inserts data for Novo

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
import csv

from json import loads

from db import DbEngine, Base, Device


# [TODO] put another scraper type
# Get parser type using argparse
parser = argparse.ArgumentParser(description='Inserts data for Novo')
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

if __name__ == "__main__":
    # saves data
    with open("inputs/%s.csv" % args.database, 'rb') as fp:
        reader = csv.DictReader(fp)

        for row in reader:
            item = Device(tac=row['tac'],
                          manufacturer=row['manufacturer'],
                          model=row['model'])
            session.add(item)
            session.commit()

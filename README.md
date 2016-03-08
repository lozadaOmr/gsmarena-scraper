#GSMArena Scraper

Scrapes data from GSMArena.

##Setup
    $ sudo apt-get update
    $ sudo apt-get install tor python-dev libxml2-dev libxslt1-dev zlib1g-dev libmysqlclient-dev mysql-server
    $ tor &
    $ make setup
    $ source env/bin/activate
    $ pip install -r requirements.txt

    Create a database table
    mysql> create user '<username>'@'localhost' identified by '<password>';
    mysql> create database <dbname>;
    mysql> grant all privileges on <dbname>.* to '<username>'@'localhost';
    mysql> flush privileges;
    mysql> exit;

##Usage
Insert rows from csv to the database table. File should be inside inputs/ with the following csv headers: tac,manufacturer,model

    $ python insert.py [-h] [--scheme SCHEME] [-u USERNAME] [-w PASSWORD] [-H HOST] [-P PORT] [-d DATABASE]

Scrape data from a url and write it in a database row

    $ python scrape.py [-h] [--scheme SCHEME] [-u USERNAME] [-w PASSWORD] [-H HOST] [-P PORT] [-d DATABASE] [-s START] [-t STOP]

Compile data from the database row and put it in a csv file. Results can be found inside results/<dbname>.csv

    $ python compile.py [-h] [--scheme SCHEME] [-u USERNAME] [-w PASSWORD] [-H HOST] [-P PORT] [-d DATABASE]

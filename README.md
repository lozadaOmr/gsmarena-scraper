#GSMArena Scraper

Scrapes data from GSMArena.

##Setup
    $ sudo apt-get update
    $ sudo apt-get install tor
    $ tor &
    $ make setup
    $ source venv/bin/activate
    $ pip install -r requirements.txt

##Usage
Add gsmarena device url page on `link` column in `filtered_urls.csv`

    $ python scraper.py

results are in `sample.csv`

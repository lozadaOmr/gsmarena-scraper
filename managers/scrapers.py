import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
from .const import DEFAULT_HEADERS
from .utils import recursive_text_content


class ScraperManager(object):
    scraper_providers = {}

    def add_scraper_provider(self, domain):
        def wrapper(fn):
            self.scraper_providers[domain] = fn
            return fn
        return wrapper

    def get_scraped_data(self, url):
        if not url:
            return None

        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

        if domain not in self.scraper_providers:
            return None

        return self.scraper_providers[domain](url)


scraper_manager = ScraperManager()


@scraper_manager.add_scraper_provider("http://www.gsmarena.com")
def gsmarena(url):
    # get response
    print "gsmarena search: %s" % url

    response = requests.get(url, headers=DEFAULT_HEADERS)

    if response.status_code != 200:
        print "warning:", response.content
        return

    soup = BeautifulSoup(response.text, 'lxml')
    data = {}

    # [TODO] change the implementation to dict type instead of list
    for t in soup.select('#specs-list table'):
        h = []

        for e in t.select('.ttl > a'):
            h.append(e.contents[0])

        c = []

        for e in t.select('.nfo'):
            if e.contents:
                c.append(e.contents[0])

        data.update(dict(zip(h, c)))

    try:
        title = soup.select('.specs-phone-name-title')[0].get_text()
    except Exception, e:
        print "warning: possible wrong link"
        return

    data.update({'Model': title})

    if 'Technology' in data:
        data['Technology'] = str(data['Technology']).strip(
            '<a class="link-network-detail collapse" href="#"></a>')

    print "return: %s" % data

    return data


@scraper_manager.add_scraper_provider("http://www.mobosdata.com")
def mobosdata(url):
    # get response
    print "mobosdata search: %s" % url

    response = requests.get(url, headers=DEFAULT_HEADERS)

    if response.status_code != 200:
        print "warning:", response.content
        return

    soup = BeautifulSoup(response.text, 'lxml')
    data = {}

    for row in soup.select('.single-phone table tr'):
        name = row.select('th')[0].contents[0]
        value = row.select('td')[0].contents

        if not value:
            value = ''
        elif str(value[0]) == '<div class="fa fa-check"></div>':
            value = True
        elif str(value[0]) == '<div class="fa fa-times"></div>':
            value = False
        else:
            value = value[0]

        data[name] = value
        data['manufacturer'] = soup.select(
                                    '.breadcrumbs > .pull-left > a + a')[0].text

    # [TODO] Create mapping to DEFAULT_FIELDNAMES
    #!---

    print "return: %s" % data

    return data


@scraper_manager.add_scraper_provider("http://www.phonearena.com")
def phonearena(url):
    # get response
    print "phonearena search: %s" % url

    response = requests.get(url, headers=DEFAULT_HEADERS)

    if response.status_code != 200:
        print "warning:", response.content
        return

    soup = BeautifulSoup(response.text, 'lxml')
    data = {}

    for row in soup.select('.s_specs_box > ul > li'):
        headers = []

        for header in row.select('strong.s_lv_1'):
            if len(header.contents):
                headers.append(header.contents[0])
                break

        name = ', '.join(recursive_text_content(headers)) \
                   .strip(':')

        # some tags can be empty
        if not name:
            continue

        value = ', '.join(recursive_text_content(
                                    row.select('> ul > li')))

        data[name] = value

    # [TODO] Create mapping to DEFAULT_FIELDNAMES
    #!---

    print "return: %s" % data

    return data

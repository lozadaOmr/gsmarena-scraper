import re
import requests
from bs4 import BeautifulSoup
from urllib import quote
from .const import DEFAULT_HEADERS


class UrlManager(object):
    url_providers = {}

    def add_url_provider(self, tag, prio=99):
        def wrapper(fn):
            self.url_providers[tag] = {
                'method': fn,
                'prio': prio,
            }

            return fn
        return wrapper

    def get_url_provider(self, tag):
        return self.url_providers.get(tag, None)

    def get_url(self, keyword=None):
        if not keyword:
            return None

        # [TODO] should return a URL from a given keyword taking note
        # of the priority
        providers = []

        for tag, provider in self.url_providers.items():
            providers.append(provider)

        # we need to sort the provider based on priority
        prio_providers = sorted(providers, key=lambda x: x['prio'])

        for provider in prio_providers:
            fn = provider.get('method')

            if not fn:
                raise Exception('provider %s is empty' % provider)

            url = fn(keyword)

            if url:
                return url


url_manager = UrlManager()


@url_manager.add_url_provider('gsmarena', 1)
def gsmarena(keyword):
    # check bing search
    manufacturer = keyword.split()[0].lower()

    domain = "http://www.gsmarena.com"
    url = "http://www.bing.com/search?q={0}&go=Submit&qs=n&form=QBRE&pq={0}" \
          "&sc=8-25&sp=-1&sk=&cvid=505D5E8D48744189BB96C5EC6FB91FB2".format(
            quote("gsmarena %s" % keyword))

    # get response
    print "bing search: gsmarena %s" % keyword

    response = requests.get(url, headers=DEFAULT_HEADERS)

    if response.status_code != 200:
        print "warning:", response.content
        return

    # check first item in the list
    soup = BeautifulSoup(response.text, 'lxml')

    for link in soup.select('#b_results li h2 > a'):
        attrs = link.__dict__.get('attrs')

        if not attrs:
            continue

        href = attrs.get('href').lower()

        if href and href.find("%s/%s" % (domain, manufacturer)) == 0:
            print "found: %s" % href

            return href


@url_manager.add_url_provider('mobosdata', 3)
def mobosdata(keyword):
    # check mobosdata search
    manufacturer = keyword.split()[0].lower()

    domain = "http://www.mobosdata.com"
    url = "{0}/search/{1}".format(domain, quote(keyword))

    # get response
    print "mobosdata search: %s" % keyword

    response = requests.get(url, headers=DEFAULT_HEADERS)

    if response.status_code != 200:
        print "warning:", response.content
        return

    # check first item in the list
    soup = BeautifulSoup(response.text, 'lxml')

    for link in soup.select('.phones.models article > a'):
        attrs = link.__dict__.get('attrs')

        if not attrs:
            continue

        href = attrs.get('href').lower()

        if href and href.strip('/').find(manufacturer) == 0:
            url = "%s%s" % (domain, href)

            print "found: %s" % url

            return url


@url_manager.add_url_provider('phonearena', 2)
def phonearena(keyword):
    # check bing search
    manufacturer = keyword.split()[0].lower()

    domain = "http://www.phonearena.com"
    url = "http://www.bing.com/search?q={0}&go=Submit&qs=n&form=QBRE&pq={0}" \
          "&sc=8-25&sp=-1&sk=&cvid=505D5E8D48744189BB96C5EC6FB91FB2".format(
            quote("phonearena %s" % keyword))

    # get response
    print "bing search: phonearena %s" % keyword

    response = requests.get(url, headers=DEFAULT_HEADERS)

    if response.status_code != 200:
        print "warning:", response.content
        return

    # check first item in the list
    soup = BeautifulSoup(response.text, 'lxml')

    for link in soup.select('#b_results li h2 > a'):
        attrs = link.__dict__.get('attrs')

        if not attrs:
            continue

        href = attrs.get('href').lower()

        if href and href.find("%s/phones/%s" % (domain, manufacturer)) == 0:
            print "found: %s" % href

            return href

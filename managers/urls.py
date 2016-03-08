import re
import requests
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
    search_keyword = "gsmarena %s" % keyword

    # use bing to search for results
    url = "http://www.bing.com/search?q={0}&go=Submit&qs=n&form=QBRE&pq={0}" \
          "&sc=8-25&sp=-1&sk=&cvid=505D5E8D48744189BB96C5EC6FB91FB2".format(
            quote(search_keyword))

    # get response
    print "bing search: %s" % search_keyword

    response = requests.get(url, headers=DEFAULT_HEADERS)

    if response.status_code != 200:
        print "warning:", response.content
        return

    # match format
    master = "http://www.gsmarena.com/%s" % keyword.split()[0].lower()
    content = response.content
    preg = 'href="%s(.*?)"' % master

    match = re.search(preg, content)

    if match:
        url = "%s%s" % (master, match.groups()[0])

        print "found: %s" % url

        return url

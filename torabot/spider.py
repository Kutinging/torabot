import requests
from urllib.parse import urlencode, urljoin
import re
from logbook import Logger
from collections import OrderedDict
from bs4 import BeautifulSoup as BS
from datetime import datetime


log = Logger(__name__)


def fetch_list(query, start):
    base = 'http://www.toranoana.jp/cgi-bin/R2/allsearch.cgi'
    return fetch(
        base + '?' + urlencode(OrderedDict([
            ('item_kind', '0401'),
            ('bl_fg', '0'),
            ('search', query.encode('Shift_JIS')),
            ('ps', start + 1),
        ])),
        headers={'Referer': base}
    )


def fetch(uri, headers={}):
    hd = {'Cookie': 'afg=0'}
    hd.update(headers)
    r = requests.get(uri, headers=hd)
    return r.content


def parse(data):
    soup = BS(data, 'html5lib')
    total, begin, end = parse_stats(soup)
    return {
        'total': total,
        'begin': begin,
        'end': end,
        'arts': parse_arts(soup)
    }


def parse_stats(soup):
    m = re.search(r'（ (\d+) 件 のうち (\d+) 〜 (\d+) 件表示）', soup.get_text())
    if not m:
        total, begin, end = 0, 0, 0
    else:
        total, begin, end = [int(m.group(i)) for i in range(1, 4)]
        # start from zero
        begin -= 1
    return total, begin, end


def parse_arts(soup):
    base = 'http://www.toranoana.jp/'
    trs = soup.select('table.FixFrame tr')
    assert len(trs) == 0 or len(trs) > 3, "wrong list length: %d" % len(trs)
    return list(map(lambda tr: {
        'title': tr.select('td.c1 a')[0].string,
        'author': tr.select('td.c2 a')[0].string,
        'comp': tr.select('td.c3 a')[0].string,
        'uri': urljoin(base, tr.select('td.c1 a')[0]['href']),
        'reserve': '予' in tr.select('td.c7')[0].get_text()
    }, trs[2:-1:2]))


def fetch_and_parse_all(query):
    d = parse(fetch_list(query, 0))
    yield from d['arts']
    while d['end'] < d['total']:
        log.info('fetch start from {}', d['end'])
        d = parse(fetch_list(query, d['end']))
        yield from d['arts']


def fetch_ptime(uri):
    soup = BS(fetch(uri))
    for td in soup.select('td.DetailData_R'):
        if td.string:
            try:
                return datetime.strptime(td.string.strip(), r'%Y/%m/%d')
            except:
                pass

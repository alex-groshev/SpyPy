#!/usr/bin/env python

import sys
import re
import random
import socket
from spypyconfig import SpyPyConfig
from spypyio import SpyPyIo
from datetime import datetime
from urllib2 import Request, urlopen, URLError, HTTPError
from BeautifulSoup import BeautifulSoup
from pymongo import MongoClient
from urlparse import urlparse


def get_random_item(list):
    return random.choice(list)

def scrape(url, user_agent):
    result = None
    headers = {'User-Agent': user_agent}
    request = Request(url, None, headers)

    try:
        urlfile = urlopen(request)
    except HTTPError, e:
        print e.code
    except URLError, e:
        print e.reason
    else:
        result = urlfile.read()
        urlfile.close()

    return result

def main(urls):
    if len(urls) < 1:
        print 'Please, specify URL(s)!'
        sys.exit(1)
    
    # Loading configs
    spypyconfig = SpyPyConfig()
    configs = spypyconfig.load('spypy.cfg')

    client = MongoClient(configs['host'], configs['port'])
    db = client.spypy
    collection = db.domains

    # Loading user agents from text file
    spypyio = SpyPyIo()
    user_agents = spypyio.get_file_contents('useragents.txt')

    for url in urls:
        url = 'http://' + url if not url.startswith('http://') else url
        content = scrape(url, get_random_item(user_agents))
        soup = BeautifulSoup(content)

        # Getting title
        title = soup.title.string
        title = title.encode('utf-8')

        # Getting description meta tag
        description = soup.find('meta', {"name": "description"})
        description = description['content'] if description != None else ''
        description = description.encode('utf-8')
        
        # Getting keywords meta tag
        keywords = soup.find('meta', {"name": "keywords"})
        if keywords != None:
            keywords = keywords['content'].split(',')
            keywords = [keyword.strip().encode('utf-8') for keyword in keywords]
        else:
            keywords = []

        # Getting Google Analytics code
        regex = re.compile(configs['google_analytics'], re.S+re.I)
        m = regex.search(content)
        google_analytics = m.group(1) if m else ''

        # Getting Google AdSense code
        regex = re.compile(configs['google_adsense'], re.S+re.I)
        m = regex.search(content)
        google_adsense = m.group(1) if m else ''

        # Getting domain name from URL
        u = urlparse(url)
        domain = u.netloc

        # Getting IP address
        ip = socket.gethostbyname(domain)

        doc = {
            'date': datetime.utcnow(),
            'domain': domain,
            'ip': ip,
            'url': url,
            'title': title,
            'description': description,
            'keywords': keywords,
            'analytics': google_analytics,
            'adsense': google_adsense,
            'processed': 1
        }

        print "Saving %s" % (domain)

        collection.insert(doc)

    print 'Done'

if __name__=='__main__':
    main(sys.argv[1:])
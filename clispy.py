#!/usr/bin/env python

import sys
import re
import random
import socket
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from urlparse import urlparse
from confspy import ConfSpyPy
from iospy import IoSpyPy
from netspy import NetSpyPy


def get_random_item(list):
    return random.choice(list)

def main(urls):
    if len(urls) < 1:
        print 'Please, specify URL(s)!'
        sys.exit(1)
    
    # Loading configs
    confspypy = ConfSpyPy()
    configs = confspypy.load('spypy.cfg')

    client = MongoClient(configs['host'], configs['port'])
    db = client.spypy
    collection = db.domains

    # Loading user agents from text file
    iospypy = IoSpyPy()
    user_agents = iospypy.file_get_contents('useragents.txt')

    netspypy = NetSpyPy()

    for url in urls:
        url = 'http://' + url if not url.startswith('http://') else url
        content = netspypy.scrape(url, get_random_item(user_agents))
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

        print 'Inserting domain: %s' % domain

        try:
            collection.insert(doc)
        except:
            print 'Error inserting domain: %s' % domain
            print 'Unexpected error:', sys.exc_info()[0], sys.exc_info()[1]

    print 'Done'

if __name__=='__main__':
    main(sys.argv[1:])
#!/usr/bin/env python

import sys
import re
import random
import socket
from datetime import datetime
from urllib2 import Request, urlopen, URLError, HTTPError
from ConfigParser import ConfigParser
from BeautifulSoup import BeautifulSoup
from pymongo import MongoClient
from urlparse import urlparse

def load_config(file):
    config = ConfigParser()
    config.read(file)

    # MongoDB settings
    host = config.get('MongoDB', 'host')
    port = config.getint('MongoDB', 'port')

    # Regex settings
    google_analytics = config.get('Regex', 'google_analytics')
    google_adsense = config.get('Regex', 'google_adsense')

    return {
        'host': host,
        'port': port,
        'google_analytics': google_analytics,
        'google_adsense': google_adsense
    }

def help(option):
    if option == 1:
        print 'Please, specify URL(s)!'
    elif option == 2:
        print 'Please, specify MongoDB and Regex parameters in spypy.cfg!'
    else:
        print 'Undefined help option!'

def get_file_contents(file):
    try:
        with open(file) as f:
            return [line.strip() for line in f]
    except EnvironmentError as err:
        print "Unable to open file: {}".format(err)
        sys.exit(1)

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
        help(1)
        exit()
    
    # Loading configs
    configs = load_config('spypy.cfg')

    if not configs['host'] or not configs['port'] or not configs['google_analytics'] or not configs['google_adsense']:
        help(2)
        exit()

    client = MongoClient(configs['host'], configs['port'])
    db = client.spypy
    collection = db.domains

    # Loading user agents from text file
    user_agents = get_file_contents('useragents.txt')

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
            'adsense': google_adsense
        }

        print "Saving %s" % (domain)

        collection.insert(doc)

    print 'Done'

if __name__=='__main__':
    main(sys.argv[1:])
#!/usr/bin/env python

import sys
import datetime
import urllib, urllib2
import re
import ConfigParser
from BeautifulSoup import BeautifulSoup
from pymongo import MongoClient

def load_config():
    config = ConfigParser.ConfigParser()
    config.read('spypy.cfg')

    # MongoDB settings
    host = config.get('MongoDB', 'host')
    port = config.getint('MongoDB', 'port')

    return {
        'host':host,
        'port':port
    }

def help_args():
    print 'Please, specify domain(s)!'

def help_config():
    print 'Please, specify MongoDB host and port parameters in spypy.cfg!'

def scrape(url):
    result = None
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0'}
    request = urllib2.Request(url, None, headers)

    try:
        urlfile = urllib2.urlopen(request)
    except HTTPError, e:
        print e.code
    except URLError, e:
        print e.reason
    else:
        result = urlfile.read()
        urlfile.close()

    return result


def main(domains):
    if len(domains) < 1:
        help_args()
        exit()
    
    # Loading configs
    configs = load_config()

    if not configs['host'] or not configs['port']:
        help_config()
        exit()

    client = MongoClient(configs['host'], configs['port'])
    db = client.spypy
    collection = db.domains

    for domain in domains:
        content = scrape('http://' + domain)
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

        doc = {
            'date': datetime.datetime.utcnow(),
            'domain': domain,
            'title': title,
            'description': description,
            'keywords': keywords
        }

        print "Inserting domain %s" % (domain)

        collection.insert(doc)

    print 'Done'

if __name__=='__main__':
    main(sys.argv[1:])
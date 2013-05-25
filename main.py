#!/usr/bin/env python

import sys
import datetime
import urllib, urllib2
import re
import random
import ConfigParser
from BeautifulSoup import BeautifulSoup
from pymongo import MongoClient

def load_config(file):
    config = ConfigParser.ConfigParser()
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

def help_args():
    print 'Please, specify domain(s)!'

def help_config():
    print 'Please, specify MongoDB and Regex parameters in spypy.cfg!'

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
    configs = load_config('spypy.cfg')

    if not configs['host'] or not configs['port'] or not configs['google_analytics'] or not configs['google_adsense']:
        help_config()
        exit()

    client = MongoClient(configs['host'], configs['port'])
    db = client.spypy
    collection = db.domains

    # Loading user agents from text file
    user_agents = get_file_contents('useragents.txt')

    for domain in domains:
        content = scrape('http://' + domain, get_random_item(user_agents))
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

        doc = {
            'date': datetime.datetime.utcnow(),
            'domain': domain,
            'title': title,
            'description': description,
            'keywords': keywords,
            'analytics': google_analytics,
            'adsense': google_adsense
        }

        print "Inserting domain %s" % (domain)

        collection.insert(doc)

    print 'Done'

if __name__=='__main__':
    main(sys.argv[1:])
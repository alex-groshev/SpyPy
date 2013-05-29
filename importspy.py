#!/usr/bin/env python

import sys
from datetime import datetime
from pymongo import MongoClient
from confspy import ConfSpyPy
from iospy import IoSpyPy


def main():
    if len(sys.argv) < 2:
        print 'Please, specify text file!'
        sys.exit(1)

    # Loading domains from text file
    iospypy = IoSpyPy()
    domains = iospypy.file_get_contents(sys.argv[1])

    # Loading configs
    confspypy = ConfSpyPy()
    configs = confspypy.load('spypy.cfg')

    client = MongoClient(configs['host'], configs['port'])
    db = client.spypy
    collection = db.domains

    for domain in domains:
        doc = {
            'date': datetime.utcnow(),
            'domain': domain,
            'ip': '',
            'url': '',
            'title': '',
            'description': '',
            'keywords': [],
            'analytics': '',
            'adsense': '',
            'processed': 0
        }

        print 'Inserting domain: %s' % domain

        try:
            collection.insert(doc)
        except:
            print 'Error inserting domain: %s' % domain
            print 'Unexpected error:', sys.exc_info()[0], sys.exc_info()[1]

    print 'Done'

if __name__=='__main__':
    main()
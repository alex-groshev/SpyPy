#!/usr/bin/env python

import sys
from datetime import datetime
from confspy import ConfSpyPy
from dataspy import DataSpyPy
from iospy import IoSpyPy


def main():
    if len(sys.argv) < 2:
        print 'Please, specify text file!'
        sys.exit(1)

    domains = IoSpyPy.file_get_contents(sys.argv[1])
    configs = ConfSpyPy.load('spypy.cfg')
    dataspypy = DataSpyPy(configs['host'], configs['port'])

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

        dataspypy.insert_record(doc)

    print 'Done'

if __name__ == '__main__':
    main()

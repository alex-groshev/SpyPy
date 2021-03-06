#!/usr/bin/env python

import sys
from confspy import ConfSpyPy
from dataspy import DataSpyPy
from procspy import ProcSpyPy


def main(urls):
    configs = ConfSpyPy.load('spypy.cfg')

    dataspypy = DataSpyPy(configs['host'], configs['port'])

    procspypy = ProcSpyPy(dataspypy, configs['google_analytics'], configs['google_adsense'])
    procspypy.process_urls(urls)

if __name__ == '__main__':
    main(sys.argv[1:])

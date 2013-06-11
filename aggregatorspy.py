#!/usr/bin/env python

import sys
from confspy import ConfSpyPy
from dataspy import DataSpyPy
from procspy import ProcSpyPy


def main():
    if len(sys.argv) < 2:
        print 'Please, specify a number of records to process!'
        sys.exit(1)
    
    confspypy = ConfSpyPy()
    configs = confspypy.load('spypy.cfg')

    dataspypy = DataSpyPy(configs['host'], configs['port'])
    records = dataspypy.get_unprocessed_records(int(sys.argv[1]))

    procspypy = ProcSpyPy(dataspypy, configs['google_analytics'], configs['google_adsense'])
    procspypy.process_records(records)

if __name__=='__main__':
    main()

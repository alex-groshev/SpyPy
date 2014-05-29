#!/usr/bin/env python

import sys
import time
import Queue
from confspy import ConfSpyPy
from dataspy import DataSpyPy
from procspy import ProcSpyPy, DocumentProcessor


def main():
    start = time.time()

    if len(sys.argv) < 2:
        print 'Please, specify a number of records to process!'
        sys.exit(1)

    configs = ConfSpyPy.load('spypy.cfg')

    dataspypy = DataSpyPy(configs['host'], configs['port'])
    procspypy = ProcSpyPy(dataspypy, configs['google_analytics'], configs['google_adsense'])
    queue = Queue.Queue()

    for i in range(4):
        dp = DocumentProcessor(queue, procspypy)
        dp.setDaemon(True)
        dp.start()

    records = dataspypy.get_unprocessed_records(int(sys.argv[1]))
    for record in records:
        queue.put(record)

    queue.join()

    print "Elapsed Time: %s" % (time.time() - start)

if __name__ == '__main__':
    main()

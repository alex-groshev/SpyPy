#!/usr/bin/env python

import sys
import pika
from bson.json_util import dumps
from confspy import ConfSpyPy
from dataspy import DataSpyPy


def main():
    if len(sys.argv) < 2:
        print 'Please, specify a number of records to enqueue and regular expression (optional)!'
        sys.exit(1)

    configs = ConfSpyPy.load('spypy.cfg')

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=configs['queue'], durable=False)

    dataspypy = DataSpyPy(configs['host'], configs['port'])
    records = dataspypy.get_unprocessed_records(int(sys.argv[1]), sys.argv[2] if len(sys.argv) == 3 else None)
    for record in records:
        channel.basic_publish(exchange='', routing_key=configs['queue'], body=dumps(record))

    connection.close()

if __name__ == '__main__':
    main()

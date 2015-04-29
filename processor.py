import sys
import pika
from bson.json_util import loads
from confspy import ConfSpyPy
from dataspy import DataSpyPy
from procspy import ProcSpyPy


def callback(ch, method, properties, body):
    try:
        configs = ConfSpyPy.load('spypy.cfg')
        dataspypy = DataSpyPy(configs['host'], configs['port'])
        procspypy = ProcSpyPy(dataspypy, configs['google_analytics'], configs['google_adsense'])
        procspypy.process_document(loads(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception, e:
        print e


def main():
    configs = ConfSpyPy.load('spypy.cfg')

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=configs['queue'], durable=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=configs['queue'])
    channel.start_consuming()


if __name__ == '__main__':
    main()
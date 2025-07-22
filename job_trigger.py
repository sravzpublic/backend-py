#!/usr/bin/env python3

import argparse, nsq, os, functools, json, tornado, json
from src.util import logger

from src.services.kafka_helpers.message_contracts import MessageContracts
logger = logger.RotatingLogger(__name__).getLogger()

def pub_message(topic, msg):
    print("Sening message on topic {0} - msg {1}".format(topic, msg))
    writer.pub(topic, msg, finish_pub1)

def finish_pub1(conn, data):
    print("Message sent, stopping timmer")
    tornado.ioloop.IOLoop.instance().stop()

if __name__ == '__main__':
    '''
        To call jobs trigger:
        pipenv shell
        # RSS Feeds
        python job_trigger.py --id 23 --topic vagrant_analytics1 --nsq-host nsqd --args [] --kwargs {}
        python job_trigger.py --id 24 --topic vagrant_analytics1 --nsq-host nsqd --args [] --kwargs '{"upload_to_db": "True"}'
        python job_trigger.py --id 25 --topic vagrant_analytics1 --nsq-host nsqd --args [] --kwargs '{"upload_to_db": "True"}'
        # Index quotes
        python job_trigger.py --id 26 --topic vagrant_analytics1 --nsq-host nsqd --args [] --kwargs '{"upload_to_db": "True"}'
        python job_trigger.py --id 27 --topic vagrant_analytics1 --nsq-host vagrant.sravz.com
        python job_trigger.py --id 28 --topic vagrant_analytics1 --nsq-host vagrant.sravz.com
        python job_trigger.py --id 29 --topic vagrant_analytics1 --nsq-host vagrant.sravz.com
        python job_trigger.py --id 43 --topic vagrant_analytics1 --nsq-host nsqd --args [] --kwargs '{"upload_to_db": "True"}'
        # Historical commodities quotes
        python job_trigger.py --id 37 --topic vagrant_analytics1 --nsq-host nsqd --args [] --kwargs '{}'
        # Historical Index quotes
        python job_trigger.py --id 39 --topic vagrant_analytics1 --nsq-host nsqd --args [] --kwargs '{}'
        python job_trigger.py --id 39 --topic production_backend-py --nsq-host nsq.sravz.com --args [] --kwargs '{}'
        # Weekly earnings
        python job_trigger.py --id 45 --topic vagrant_analytics1 --nsq-host nsqd --args []  --kwargs '{"upload_to_db": "True"}'
        # Upload historical stock quotes from eod
        python job_trigger.py --id 46 --topic vagrant_analytics1 --nsq-host nsqd --args []  --kwargs '{}'
    '''
    parser = argparse.ArgumentParser(description='Submit job messages to NSQ')
    parser.add_argument('--id', dest='id', type=int, help='mesasge ID')
    parser.add_argument('--topic', type=str, default=os.environ.get('nsq_topic', None))
    parser.add_argument('--nsq-host', dest='nsq_host', default=os.environ.get('NSQ_HOST', None))
    parser.add_argument('--args', dest='args', type=str)
    parser.add_argument('--kwargs', dest='kwargs', type=str)
    parser.add_argument('--cache_message', dest='cache_message', type=bool, default=False)
    args = vars(parser.parse_args())
    topic = args['topic']
    NSQ_HOST = args["nsq_host"]
    message_id = args["id"]
    args_param = json.loads(args["args"]) if args["args"] else []
    kwargs_param = json.loads(args["kwargs"]) if args["kwargs"] else {}
    cache_message = args["cache_message"]
    logger.info('Publishing to host: {0} at topic: {1} - {2}'.format(NSQ_HOST, topic, ['{0}:4150'.format(NSQ_HOST)]))
    writer = nsq.Writer(nsqd_tcp_addresses=['{0}:4150'.format(NSQ_HOST)])
    msg = {"id":message_id,"p_i":{"args":args_param,"kwargs":kwargs_param}, "t_o": "", "cache_message": cache_message}
    logger.info("Sending message {0}".format(msg))
    callback = functools.partial(pub_message, topic=topic, msg=json.dumps(msg).encode())
    tornado.ioloop.PeriodicCallback(callback, 1000).start()
    nsq.run()
    logger.info("Message sent")
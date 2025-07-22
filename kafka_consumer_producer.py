#!/usr/bin/env python
#
# Copyright 2016 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse, os, sys, traceback, json, msgpack, datetime, base64, zlib, time
from src.services.kafka_helpers.verifiable_client import VerifiableClient
from src.services.kafka_helpers.verifiable_consumer import VerifiableConsumer
from src.services.kafka_helpers.verifiable_producer import VerifiableProducer
from confluent_kafka import Producer, KafkaError, KafkaException
from src.services.kafka_helpers import message_parser
from src.util import settings, logger


def get_producer(args):
    conf = {'broker.version.fallback': '0.9.0',
            'default.topic.config': dict()}

    VerifiableClient.set_config(conf, args)

    vp = VerifiableProducer(conf)

    #vp.dbg('Producing %d messages at a rate of %d/s' % (vp.max_msgs, throughput))

    return vp


def encode_datetime(obj):
    if isinstance(obj, datetime):
        obj = {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f").encode()}
    return obj

def deflate_and_base64_encode( string_val ):
    zlibbed_str = zlib.compress( string_val )
    compressed_string = zlibbed_str[2:-1]
    return base64.b64encode(compressed_string )

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Verifiable Python Consumer')
    parser.add_argument('--topic', action='append', type=str, default=os.environ.get('kafka_topic', None))
    parser.add_argument('--group-id', dest='group.id', default=os.environ.get('kafka_group_id', None))
    parser.add_argument('--broker-list', dest='bootstrap.servers', default=os.environ.get('kafka_broker_list', None))
    parser.add_argument('--session-timeout', type=int, dest='session.timeout.ms', default=6000)
    parser.add_argument('--enable-autocommit', action='store_true', dest='enable.auto.commit', default=False)
    parser.add_argument('--max-messages', type=int, dest='max_messages', default=-1)
    parser.add_argument('--assignment-strategy', dest='partition.assignment.strategy')
    parser.add_argument('--reset-policy', dest='topic.auto.offset.reset', default='earliest')
    parser.add_argument('--consumer.config', dest='consumer_config')
    args = vars(parser.parse_args())
    _logger = logger.RotatingLogger(__name__).getLogger()

    conf = {'broker.version.fallback': '0.9.0',
            'default.topic.config': dict()}

    VerifiableClient.set_config(conf, args)

    vc = VerifiableConsumer(conf)
    vc.use_auto_commit = args['enable.auto.commit']
    vc.max_msgs = args['max_messages']

    _logger.info('Using config: %s'%(conf))
    _logger.info('Subscribing to %s' % args['topic'])

    vc.consumer.subscribe(args['topic'],
                          on_assign=vc.on_assign, on_revoke=vc.on_revoke)

    msg_parser = message_parser.MessageParser()

    vp = get_producer(args)

    try:
        while vc.run:
            msg = vc.consumer.poll(timeout=1.0)
            if msg is None:
                # Timeout.
                # Try reporting consumed messages
                vc.send_records_consumed(immediate=True)
                # Commit every poll() timeout instead of on every message.
                # Also commit on every 1000 messages, whichever comes first.
                vc.do_commit(immediate=True)
                continue
            # Handle message (or error event)
            try:
                if msg.value():
                    _logger.info('Received message %s'%(msg.value()))
                    in_msg = msg_parser.get_input_message(msg.value())
                    _logger.info('Input Message %s'%(in_msg))
                    out_msg = msg_parser.get_output_message(in_msg)
                    _logger.info('Output Message %s'%(out_msg))
                    topic_out = out_msg.get("t_o")
                    if topic_out:
                        try:
                            _logger.debug("Sending output on topic: %s msg: %s"%(topic_out, out_msg))
                            vp.producer.produce(topic_out, value=json.dumps(out_msg))
                        except KafkaException as e:
                            _logger.error('produce() #failed: %s' % (str(e)), exc_info=True)
                        except BufferError:
                            _logger.error('Local produce queue full', exc_info=True)
                            vp.producer.poll(timeout=0.5)
                    vc.send(out_msg)
            except:
                vc.send(traceback.print_exc())
            vc.do_commit(immediate=True)
            #vc.msg_consume(msg)

    except KeyboardInterrupt:
        pass

    _logger.info('Closing consumer')
    #vc.send_records_consumed(immediate=True)
    if not vc.use_auto_commit:
        vc.do_commit(immediate=True, async=False)

    vc.consumer.close()

    vc.send({'name': 'shutdown_complete'})

    vc.dbg('All done')


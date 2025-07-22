import argparse, os, sys, traceback, json, msgpack, datetime, base64, zlib, time, ssl, nsq, functools
from src.services.kafka_helpers import message_parser
from src.util import settings, logger
from src.util.settings import constants
from functools import wraps
import errno
import os
import random
import signal
import nest_asyncio
nest_asyncio.apply()

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


writer = None
NSQ_HOST = None
msg_parser = message_parser.MessageParser()


def finish_pub(conn, data, topic, msg):
    if isinstance(data, nsq.Error):
        _logger.info('Published message %s'%(data))
        _logger.info('Reconnecting...')
        writer = nsq.Writer([NSQ_HOST])
        # try to re-pub message again if pub failed
        writer.pub(topic, msg)
        _logger.info('Published message after reconnect %s'%(data))
    else:
        _logger.info('Published message %s'%(data))

@timeout(constants.NSQ_MESSAGE_PROCESSING_TIMEOUT_SECS)
def get_output_message(in_msg):
    return msg_parser.get_output_message(in_msg)

def handler(message):
    try:
        msg = message.body.decode()
        _logger.info('NSQ Reader: Received message %s'%(msg))
        in_msg = msg_parser.get_input_message(msg)
        _logger.info('NSQ Reader: Input Message %s'%(in_msg))
        try:
            out_msg = get_output_message(in_msg)
        except TimeoutError:
            _logger.error('Timeout for message %s'%(in_msg))
        _logger.info('NSQ Reader/Writer: Output Message to be sent by Writer %s'%(out_msg))
        topic_out = in_msg.get("t_o")
        message.finish()
        if topic_out:
            _logger.debug("NSQ Writer: Sending output on topic: %s msg: %s"%(topic_out, out_msg))
            callback = functools.partial(finish_pub, topic=topic_out, msg=msg)
            writer.pub(topic_out, json.dumps(out_msg).encode(), callback)
    except:
        logger.logging.exception("Producer/Consumer error")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NSQ Python Producer/Consumer')
    parser.add_argument('--nsqd-host', dest='nsq_host', default=os.environ.get('NSQ_HOST', None))
    parser.add_argument('--nsq-lookupd-host', dest='nsq_lookupd_host', default=os.environ.get('NSQ_LOOKUPD_HOST', None))
    args = vars(parser.parse_args())
    _logger = logger.RotatingLogger(__name__).getLogger()
    NSQ_HOST = args["nsq_host"]
    if not NSQ_HOST:
        raise Exception(f"NSQ_HOST not provided {os.environ.get('NSQ_HOST')}")
    NSQ_HOST = NSQ_HOST.split(",")[random.randint(0,len(NSQ_HOST.split(","))-1)]
    if not os.environ.get('NODE_ENV'):
        raise Exception(f"Cannot determine topic: NODE_ENV not provided {os.environ.get('NODE_ENV')}")
    topic = f"{os.environ.get('NODE_ENV', None)}_backend-py"
    _logger.info('Subscribing to nsqd at {0} topic {1}'.format(NSQ_HOST, topic))
    writer = nsq.Writer([NSQ_HOST])
    nsq_lookupd_host = args["nsq_lookupd_host"]
    if not nsq_lookupd_host:
        raise Exception(f"NSQ_LOOKUPD_HOST not provided {os.environ.get('NSQ_LOOKUPD_HOST')}")
    lookupd_http_address = args["nsq_lookupd_host"].split(",")
    r = nsq.Reader(message_handler=handler,
            lookupd_http_addresses=lookupd_http_address,
            topic=topic,
            channel=topic,
            max_in_flight=10,
            # tls_v1=True,
            # tls_options={
            #     'cert_reqs': ssl.CERT_NONE,
            #     'ssl_version': ssl.PROTOCOL_TLSv1,
            #     'certfile': '/tmp/cert.pem',
            #     'keyfile': '/tmp/key.key',
            #     # 'ca_certs': '/tmp/nsqtmp/CAroot.pem',
            # },
            lookupd_request_timeout=15,
            lookupd_poll_interval=1)
    _logger.info('Subscribed to nsqd at {0} topic {1}'.format(NSQ_HOST, topic))
    nsq.run()


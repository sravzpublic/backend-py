'''
Created on Jan 9, 2017

@author: admin
'''

from diskcache import FanoutCache
from src.util import settings
from datetime import datetime, date, timedelta, time
import bson
import msgpack
import pandas as pd
import zlib
from io import StringIO


def seconds_till_midnight():
    tomorrow = date.today() + timedelta(1)
    midnight = datetime.combine(tomorrow, time())
    now = datetime.now()
    return (midnight - now).seconds

def decode_data(obj):
    if '__datetime__' in obj:
        obj = datetime.strptime(obj['as_str'].decode(), "%Y%m%dT%H:%M:%S.%f")
    elif '__objectid__' in obj:
        obj = bson.objectid.ObjectId(obj['as_str'].decode())
    elif '__dataframe__' in obj:
        obj = pd.read_csv(StringIO(obj['csv']))
    return obj

def encode_data(obj):
    if isinstance(obj, datetime):
        obj = {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f").encode()}
    elif isinstance(obj, bson.objectid.ObjectId):
        obj = {'__objectid__': True, 'as_str': str(obj).encode()}
    elif isinstance(obj, pd.core.frame.DataFrame):
        obj = {'__dataframe__': True, 'csv': obj.to_csv()}
    return obj

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


class FileCacheMe(object):
    def __init__(self, *args, **kwargs):
        self.key = kwargs.get("key")
        self.expiry = kwargs.get("expiry")

    def __call__(self, func):
        def inner(*args, **kwargs):
            cache = Cache.Instance()
            value = cache.get(self.key)
            if not value:
                value = func(*args, **kwargs)
                cache.add(self.key, value)
            return value
        return inner


@Singleton
class Cache():
    def __init__(self):
        conf = settings.constants.get_cache_config()
        self._cache = FanoutCache( conf['dir'], conf['shards'], conf['timeout'])

    @property
    def cache(self):
        return self._cache

    def add(self, key, value, expire=seconds_till_midnight(), save_as_msgpack = True):
        if save_as_msgpack:
            self._cache.add(key,  zlib.compress(msgpack.packb(value, default=encode_data)))
        else:
            self._cache.add(key,  zlib.compress(value))


    def get(self, key, json=True):
        data = self._cache.get(key)
        if data:
            if json:
                data = msgpack.unpackb(zlib.decompress(data), object_hook=decode_data)
            else:
                json.loads(msgpack.unpackb(zlib.decompress(data), object_hook=decode_data))
        return data


    def update(self, key, value):
        self._cache.pop(key)
        self.add(key, value)

    def remove_all(self):
        '''
            >>>from src.services.cache import Cache
            >>>c = Cache.Instance()
            >>>c.remove_all()
        '''
        self._cache.clear()



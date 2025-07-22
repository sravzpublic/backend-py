import os
from datetime import datetime
from src.util import settings, helper, logger
from src.services.cache import Cache
from src.services import aws
import json
import datetime
import hashlib
import numpy as np
import pandas as pd
from decorator import decorator


LOGGER = logger.RotatingLogger(__name__).getLogger()

@decorator
def save_file_to_s3(func, *args, **kwargs):
    aws_cache_engine = engine()
    aws_engine = aws.engine()
    aws_key = helper.get_md5_of_string(
        "{0}_{1}_{2}".format(func.__name__, args, kwargs))
    # = hashlib.md5(key.encode())
    bucket_name = settings.constants.pca_scatter_plot_bucket_name
    file_path = func(*args, **kwargs)
    aws_cache_engine.upload_file_to_aws(
        bucket_name, aws_key, file_path)
    return {'bucket_name': bucket_name,
            'key_name': aws_key,
            'data': None,
            'signed_url': aws_engine.get_signed_url(bucket_name, aws_key)}

@decorator
def save_file_to_s3_monthly(func, *args, **kwargs):
    aws_cache_engine = engine()
    aws_engine = aws.engine()
    # = hashlib.md5(key.encode())
    bucket_name = settings.constants.sravz_monthly_bucket_name
    file_path,aws_key = func(*args, **kwargs)
    aws_cache_engine.upload_file_to_aws(
        bucket_name, aws_key, file_path)
    return {'bucket_name': bucket_name,
            'key_name': aws_key,
            'data': None,
            'signed_url': aws_engine.get_signed_url(bucket_name, aws_key)}

class engine(object):

    def __init__(self):
        self.aws_engine = aws.engine()
        self.logger = logger.RotatingLogger(__name__).getLogger()

    def upload_stats_to_aws(self, bucket_name, key_name, data,
                            expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY):
        self.aws_engine.upload_if_object_not_found(bucket_name,
                                                   key_name, data)

    def upload_file_to_aws(self, bucket_name, key_name, file_path,
                           expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY):
        self.logger.info("Uploading file: {0} to bucket: {1} key: {2}".format(
            file_path, bucket_name, key_name))
        self.aws_engine.upload_if_file_not_found(
            bucket_name, key_name, helper.convert(file_path))

    def upload_file_to_contabo(self, bucket_name, key_name, file_path):
        self.logger.info("Uploading file: {0} to bucket: {1} key: {2}".format(
            file_path, bucket_name, key_name))
        self.aws_engine.upload_file_to_contabo( bucket_name, key_name, helper.convert(file_path))

    def upload_data_to_contabo(self, bucket_name, data, key_name, gzip_data = True, ContentType='Application/json'):
        self.aws_engine.upload_to_bucket_contabo(bucket_name,
                                                   key_name, data, gzip_data = gzip_data, ContentType=ContentType)

    def handle_cache_aws(self, cache_key, bucket_name, aws_key, data_function, upload_to_aws, orient='split'):
        value = Cache.Instance().get(cache_key)
        if not (isinstance(value, pd.core.frame.DataFrame) or value):
            value = data_function()
            Cache.Instance().add(cache_key, value)
        if upload_to_aws:
            if isinstance(value, pd.core.frame.DataFrame):
                # Covert all data frames to orient table
                if orient:
                    value = value.to_json(date_format='iso', orient=orient).replace(
                        "T00:00:00.000Z", "")
                else:
                    value = value.to_json(date_format='iso').replace(
                        "T00:00:00.000Z", "")
                self.upload_stats_to_aws(bucket_name, aws_key, json.dumps(
                    value, cls=helper.DatesEncoder))
                return {'bucket_name': bucket_name,
                        'key_name': aws_key,
                        'data': value,
                        'signed_url': self.aws_engine.get_signed_url(bucket_name, aws_key)}
            if isinstance(value, dict):
                # Check if any file provided, upload the file and change the file value with signed url
                for key, item in value.items():
                    if (isinstance(item, bytes) or isinstance(item, str)) and os.path.isfile(item):
                        aws_key_for_file = "{0}_{1}".format(
                            aws_key, helper.convert(key))
                        self.upload_file_to_aws(
                            bucket_name, aws_key_for_file, item)
                        value[key] = self.aws_engine.get_signed_url(
                            bucket_name, aws_key_for_file)
                    if isinstance(item, pd.core.frame.DataFrame):
                        # Covert all data frames to orient table
                        if orient:
                            value[key] = value.to_json(
                                date_format='iso', orient=orient).replace("T00:00:00.000Z", "")
                        else:
                            value[key] = value.to_json(
                                date_format='iso').replace("T00:00:00.000Z", "")
            # Upload the passed dict to S3
            self.upload_stats_to_aws(bucket_name, aws_key, json.dumps(
                helper.convert(value), cls=helper.DatesEncoder))
            return {'bucket_name': bucket_name,
                    'key_name': aws_key,
                    'data': value,
                    'signed_url': self.aws_engine.get_signed_url(bucket_name, aws_key)}
        else:
            return value

import boto3
import gzip
import io
import json
import os
from boto3.s3.transfer import S3Transfer, TransferConfig
from botocore.exceptions import ClientError
import pandas as pd
from src.util import settings, logger, helper
from src.services.cache import Cache
import botocore, datetime
import json

LOGGER = logger.RotatingLogger(__name__).getLogger()

def default(obj):
    if isinstance(obj, datetime.datetime):
        return { '_isoformat': obj.isoformat() }
    return super().default(obj)

def object_hook(obj):
    _isoformat = obj.get('_isoformat')
    if _isoformat is not None:
        return datetime.datetime.fromisoformat(_isoformat)
    return obj


class engine(object):
    """description of class"""

    def __init__(self):
        self.s3 = boto3.client('s3')
        self.s3Resource = boto3.resource('s3')
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.s3_contabo = boto3.client('s3',
        endpoint_url=helper.settings.constants.CONTABO_URL,
        aws_access_key_id=helper.settings.constants.CONTABO_KEY,
        aws_secret_access_key=helper.settings.constants.CONTABO_SECRET)
        self.s3_contabo_any_bucket = boto3.client('s3',
        endpoint_url=helper.settings.constants.CONTABO_BASE_URL,
        aws_access_key_id=helper.settings.constants.CONTABO_KEY,
        aws_secret_access_key=helper.settings.constants.CONTABO_SECRET)
        self.s3_idrivee2 = boto3.client('s3',
        endpoint_url=helper.settings.constants.IDRIVEE2_BASE_URL,
        aws_access_key_id=helper.settings.constants.IDRIVEE2_KEY,
        aws_secret_access_key=helper.settings.constants.IDRIVEE2_SECRET)

    def get_contabo_boto3_session(self):
        """
        Returns a boto3 session configured for Contabo S3-compatible storage.
        """
        session = boto3.Session(
            aws_access_key_id=settings.constants.CONTABO_KEY,
            aws_secret_access_key=settings.constants.CONTABO_SECRET
        )
        return session

    def set_cors(self, bucket_name):
        '''
            from src.services import aws
            ae = aws.engine()
            ae.set_cors('sravz-scatter-plot-pca')
            ae.set_cors('sravz-components-pca')
        '''
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        cors = bucket.Cors()
        config = {
            'CORSRules': [{
                'AllowedMethods': ['GET'],
                'AllowedOrigins': ['*'],
                'AllowedHeaders': ['*'],
                'MaxAgeSeconds': 3000
            }]}
        cors.put(CORSConfiguration=config)

    def check_bucket_exists(self, bucket_name):
        try:
            self.s3.head_bucket(Bucket=bucket_name)
            return True
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 403:
                print("Private Bucket. Forbidden Access!")
                return True
            elif error_code == 404:
                print("Bucket Does Not Exist!")
                return False

    def get_bucket_keys(self, bucket_name):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        for object in bucket.objects.all():
            print(object)

    def upload_to_bucket_contabo(self, bucket_name, key, data, expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY, 
                                 ContentType='Application/json', gzip_data=True):
        content_encoding = 'utf-8'
        if bucket_name and data:
            if gzip_data:
                out = io.BytesIO()
                with gzip.GzipFile(fileobj=out, mode="w") as f:
                    f.write(data.encode())
                data = out.getvalue()
                content_encoding = 'gzip'
            LOGGER.warning(f"Uploaded file to contabo bucket: {bucket_name} Key - {key}")
            self.s3_contabo_any_bucket.put_object(Bucket=bucket_name, Key=key, Body=data, 
                                                Expires=expires, ContentType=ContentType,
                                                ContentEncoding=content_encoding)
        else:
            LOGGER.info(f"Bucket name: {bucket_name} or data null. No uploaded to contabo")

    def delete_from_bucket_contabo(self, bucket_name, key):
        self.s3_contabo_any_bucket.delete_object(Bucket=bucket_name, Key=key)

    def upload_to_bucket_idrive2e(self, bucket_name, key, data, expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY, 
                                 ContentType='Application/json', gzip_data=True):
        content_encoding = 'utf-8'
        if bucket_name and data:
            if gzip_data:
                out = io.BytesIO()
                with gzip.GzipFile(fileobj=out, mode="w") as f:
                    f.write(data.encode())
                data = out.getvalue()
                content_encoding = 'gzip'
            LOGGER.warning(f"Uploaded file to idrivee2 bucket: {bucket_name} Key - {key}")
            self.s3_idrivee2.put_object(Bucket=bucket_name, Key=key, Body=data, 
                                                Expires=expires, ContentType=ContentType,
                                                ContentEncoding=content_encoding,
                                                ContentLength=len(data))
        else:
            LOGGER.info(f"Bucket name: {bucket_name} or data null. No uploaded to contabo")

    def delete_from_bucket_idrive2e(self, bucket_name, key):
        self.s3_idrivee2.delete_object(Bucket=bucket_name, Key=key)

    def upload_to_bucket(self, bucket_name, key, data, expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY, gzip_data=False):
        content_encoding = None
        if bucket_name and data:
            if not self.check_bucket_exists(bucket_name):
                self.s3.create_bucket(Bucket=bucket_name)
                self.set_cors(bucket_name)
            if gzip_data:
                out = io.BytesIO()
                with gzip.GzipFile(fileobj=out, mode="w") as f:
                    f.write(data.encode())
                data = out.getvalue()
                content_encoding = 'gzip'
            if expires:
                self.s3.put_object(Bucket=bucket_name, 
                                   Key=key, Body=data, 
                                   Expires=expires, 
                                   ContentType='Application/json',
                                   ContentEncoding=content_encoding)
            else:
                self.s3.put_object(Bucket=bucket_name, Key=key, Body=data, ContentType='Application/json',
                                ContentEncoding=content_encoding)

    def download_object(self, bucket_name, key, gzip_data = False):
        self.logger.info(
            'Download Key:{0} From Bukect: {1}'.format(key, bucket_name))
        data = self.s3.get_object(Bucket=bucket_name, Key=key)
        if gzip_data:
            bytestream = io.BytesIO(data['Body'].read())
            return gzip.GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')
        return data['Body'].read()

    def download_object_contabo(self, bucket_name, key, gzip_data = False):
        self.logger.info(
            'Download Key:{0} From Bucket: {1}'.format(key, bucket_name))
        data = self.s3_contabo_any_bucket.get_object(Bucket=bucket_name, Key=key)
        if gzip_data:
            bytestream = io.BytesIO(data['Body'].read())
            return gzip.GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')
        return data['Body'].read()

    def download_object_idrivee2(self, bucket_name, key, gzip_data = False):
        self.logger.info(
            'Download Key:{0} From Bucket: {1}'.format(key, bucket_name))
        data = self.s3_idrivee2.get_object(Bucket=bucket_name, Key=key)
        if gzip_data:
            bytestream = io.BytesIO(data['Body'].read())
            return gzip.GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')
        return data['Body'].read()


    def key_exists(self, bucket_name, key_name):
        '''
            get_key('sravz-commodities', 'gold_2017-01-17'):
        '''
        try:
            self.s3.head_object(Bucket=bucket_name, Key=key_name)

        except:
            return False
        return True

    def get_uploaded_objects_list(self, bucket_name):
        '''
            from src.services import aws
            ae = aws.engine()
            ae.get_uploaded_objects_list('sravz-historical-rolling-stats')
            ae.get_uploaded_objects_list('sravz-scatter-plot-pca')
        '''
        return Cache.Instance().get('%s' % (bucket_name))

    def update_uploaded_objects_list(self, bucket_name, key_name):
        object_list = self.get_uploaded_objects_list(bucket_name)
        if object_list:
            object_list.append(key_name)
        else:
            object_list = [key_name]
        Cache.Instance().update('%s' % (bucket_name), object_list)

    def is_key_in_uploaded_objects_list(self, bucket_name, key_name):
        object_list = self.get_uploaded_objects_list(bucket_name)
        return object_list and (key_name.encode() in object_list)

    def upload_if_object_not_found(self, bucket_name, key_name, data, expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY,
                                   gzip_data=True):
        '''
            upload_if_object_not_found('sravz-historical-rolling-stats', 'gold_2017-01-17')
        '''
        if not data:
            raise ValueError("Data to upload is null")
        if not self.is_key_in_uploaded_objects_list(bucket_name, key_name):
            self.upload_to_bucket(bucket_name, key_name,
                                  data, expires=expires, gzip_data=gzip_data)
            self.update_uploaded_objects_list(bucket_name, key_name)

    def upload_if_object_not_found_contabo(self, bucket_name, key_name, data, expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY,
                                   gzip_data=True):
        '''
            upload_if_object_not_found('sravz-historical-rolling-stats', 'gold_2017-01-17')
        '''
        if not data:
            raise ValueError("Data to upload is null")
        self.upload_to_bucket(bucket_name, key_name,
                                data, expires=expires, gzip_data=gzip_data)

    def upload_if_file_not_found(self, bucket_name, key_name, file_path, expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY):
        '''
            upload_if_file_not_found('sravz-historical-rolling-stats', 'gold_2017-01-17')
        '''
        if not file_path or not os.path.isfile(file_path):
            if not self.is_key_in_uploaded_objects_list(bucket_name, key_name):
                raise ValueError("file {0} is null or not provided and bucket {1} key {2} not uploaded".format(
                    file_path, bucket_name, key_name))
        if bucket_name and not self.is_key_in_uploaded_objects_list(bucket_name, key_name):
            if not self.check_bucket_exists(bucket_name):
                self.s3.create_bucket(Bucket=bucket_name)
                self.set_cors(bucket_name)
            transfer = S3Transfer(self.s3)
            transfer.upload_file(file_path, bucket_name, key_name)
            self.update_uploaded_objects_list(bucket_name, key_name)
            if settings.constants.DEVICE_TYPE_MOBILE_DELETE_IMAGE_FILES:
                os.remove(file_path)

    def upload_file_to_contabo(self, bucket_name, key_name, file_path, target=settings.constants.S3_TARGET_CONTABO):
        '''
            upload_if_file_not_found('sravz-historical-rolling-stats', 'gold_2017-01-17')
        '''
        transfer = None
        config = TransferConfig(multipart_threshold=10 * 1024 * 1024)  # Multipart for files over 10MB
        if target==settings.constants.S3_TARGET_CONTABO:
            transfer = S3Transfer(self.s3_contabo_any_bucket, config)            
        elif target==settings.constants.S3_TARGET_IDRIVEE2:
            transfer = S3Transfer(self.s3_idrivee2, config)            
        if transfer:
            transfer.upload_file(file_path, bucket_name, key_name)            
            # self.s3_contabo_any_bucket.upload_file(file_path, bucket_name, key_name)            
        if settings.constants.DEVICE_TYPE_MOBILE_DELETE_IMAGE_FILES:
            os.remove(file_path)

    def download_file_from_s3(self, bucket_name, key_name, file_path, target=settings.constants.S3_TARGET_CONTABO):
        """
        Download a file from Contabo S3-compatible storage to a local file.
        """
        if target == settings.constants.S3_TARGET_CONTABO:
            s3_client = self.s3_contabo_any_bucket
        elif target == settings.constants.S3_TARGET_IDRIVEE2:
            s3_client = self.s3_idrivee2
        else:
            s3_client = self.s3

        try:
            s3_client.download_file(bucket_name, key_name, file_path)
            self.logger.info(f"Downloaded file from {bucket_name}/{key_name} to {file_path}")
        except Exception as e:
            self.logger.exception(f"Failed to download file from {bucket_name}/{key_name} to {file_path}: {e}")
            
    def get_signed_url(self, bucket_name, key_name, expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY):
        '''
            from src.services import aws
            ae = aws.engine()
            ae.get_signed_url('sravz-scatter-plot-pca', 'get_scatter_plot_data_pca_by_timeframe_ca5a409ff93a9271dbfd02eaae62d7c5_10')
        '''
        # if not self.key_exists(bucket_name, key_name):
        #    raise ValueError("Bucket (%s) or Key (%s) does not exists. Cannot create signed URL"%(bucket_name, key_name))
        return self.s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key_name,
            },
            # Expire in 2 days
            ExpiresIn=172800
        )


    def upload_stats_to_aws(self, bucket_name, key_name, data,
                            expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY):
        self.upload_if_object_not_found(bucket_name, key_name, data)

    def handle_cache_aws(self, cache_key, bucket_name, aws_key, data_function, upload_to_aws):
        value = Cache.Instance().get(cache_key)
        if not (isinstance(value, pd.core.frame.DataFrame) or value):
            value = data_function()
            Cache.Instance().add(cache_key, value)
        if upload_to_aws:
            if isinstance(value, pd.core.frame.DataFrame):
                value = value.to_json(date_format='iso', orient='split').replace(
                    "T00:00:00.000Z", "")
            self.upload_stats_to_aws(bucket_name, aws_key, json.dumps(
                helper.convert(value), cls=helper.DatesEncoder))
        return {'bucket_name': bucket_name,
                'key_name': aws_key,
                'data': value,
                'signed_url': self.get_signed_url(bucket_name, aws_key)}

    def apply_life_cycle_policy_to_all_buckets(self):
        for bucket in settings.constants.AWS_BUCKETS:
            self.apply_life_cycle_policy(bucket)

    def apply_life_cycle_policy(self, bucket_name):
        try:
            policy_status = self.s3.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={
                    'Rules': [
                        {
                            'Expiration': {
                                'Days': 2,
                            },
                            'ID': 'delete-after-2-days',
                            'Prefix': '',
                            'Status': 'Enabled'
                        },
                    ]
                }
            )
            self.logger.info("Policy applied to bucket: {0} \nReason:{1}".format(
                bucket_name, policy_status))
        except Exception as e:
            self.logger.exception(
                "Unable to apply bucket policy. bucket_name {0} \nReason:{1}".format(bucket_name, e))

    def apply_30_days_life_cycle_policy(self, bucket_name = 'sravz-monthly'):
        try:
            policy_status = self.s3.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={
                    'Rules': [
                        {
                            'Expiration': {
                                'Days': 30,
                            },
                            'ID': 'delete-after-30-days',
                            'Prefix': '',
                            'Status': 'Enabled'
                        },
                    ]
                }
            )
            self.logger.info("Policy applied to bucket: {0} \nReason:{1}".format(
                bucket_name, policy_status))
        except Exception as e:
            self.logger.exception(
                "Unable to apply bucket policy. bucket_name {0} \nReason:{1}".format(bucket_name, e))

    def is_quote_updated_today(self, collection_name, provider = settings.constants.S3_TARGET_AWS):
        '''
            from src.services import aws
            ae = aws.engine()
            ae.is_quote_updated_today('fund_us_jbalx')            
        '''
        try:        
            key = f"{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{collection_name}.json"        
            response = None
            if provider == settings.constants.S3_TARGET_AWS:
                response = self.s3.head_object(Bucket=settings.constants.SRAVZ_DATA_S3_BUCKET, Key=key)
            elif provider == settings.constants.S3_TARGET_CONTABO:
                response = self.s3_contabo_any_bucket.head_object(Bucket=settings.constants.SRAVZ_DATA_S3_BUCKET, Key=key)
            elif provider == settings.constants.S3_TARGET_IDRIVEE2:
                response = self.s3_idrivee2.head_object(Bucket=settings.constants.SRAVZ_DATA_S3_BUCKET, Key=key)
            last_update_time = response['LastModified']        
            current_date = datetime.datetime.now(datetime.timezone.utc).date()
            # self.logger.debug("Upload timestamp: %s - Current Timestamp %s", last_update_time, current_date)        
            if last_update_time.date() == current_date:
                return True
            return False
        except Exception as e:
            self.logger.exception(
                "S3 Key not found {0} \nReason:{1}".format(collection_name, e))
            return False
            
    def is_file_uploaded_today(self, bucket, key, provider = settings.constants.S3_TARGET_AWS):
        '''
            from src.services import aws
            ae = aws.engine()
            ae.is_quote_updated_today('fund_us_jbalx')            
        '''
        try:             
            response = None
            if provider == settings.constants.S3_TARGET_AWS:
                response = self.s3.head_object(Bucket=bucket, Key=key)
            elif provider == settings.constants.S3_TARGET_CONTABO:
                response = self.s3_contabo_any_bucket.head_object(Bucket=bucket, Key=key)
            elif provider == settings.constants.S3_TARGET_IDRIVEE2:
                response = self.s3_idrivee2.head_object(Bucket=bucket, Key=key)
            last_update_time = response['LastModified']        
            current_date = datetime.datetime.now(datetime.timezone.utc).date()
            # self.logger.debug("Upload timestamp: %s - Current Timestamp %s", last_update_time, current_date)        
            if last_update_time.date() == current_date:
                return True
            return False
        except Exception as e:
            self.logger.exception(
                "S3 Key not found Bucket {0} - Key {1} \nReason:{1}".format(bucket, key))
            return False

    def is_file_uploaded_n_days_back(self, bucket, key, days_back, provider = settings.constants.S3_TARGET_AWS):
        '''
            from src.services import aws
            ae = aws.engine()
            ae.is_quote_updated_today('fund_us_jbalx')            
        '''
        try:             
            response = None
            if provider == settings.constants.S3_TARGET_AWS:
                response = self.s3.head_object(Bucket=bucket, Key=key)
            elif provider == settings.constants.S3_TARGET_CONTABO:
                response = self.s3_contabo_any_bucket.head_object(Bucket=bucket, Key=key)
            elif provider == settings.constants.S3_TARGET_IDRIVEE2:
                response = self.s3_idrivee2.head_object(Bucket=bucket, Key=key)
            last_update_time = response['LastModified']        
            current_date = datetime.datetime.now(datetime.timezone.utc).date()
            date_n_days_back = current_date - datetime.timedelta(days=days_back)

            # self.logger.debug("Upload timestamp: %s - Current Timestamp %s", last_update_time, current_date)        
            if last_update_time.date() <= date_n_days_back:
                return True
            return False
        except Exception as e:
            self.logger.exception(
                "S3 Key not found Bucket {0} - Key {1} \nReason:{1}".format(bucket, key))
            return False
                
    def upload_quotes_to_s3(self, data, collection_name):
        self.upload_to_bucket(settings.constants.SRAVZ_DATA_S3_BUCKET,
        f"{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{collection_name}.json",
        json.dumps(data, default=default), gzip_data=True)

    def upload_quotes_to_contabo(self, data, collection_name, 
                                 prefix=None, 
                                 target=settings.constants.S3_TARGET_CONTABO):
        key = prefix if prefix else f"{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{collection_name}.json"
        if target==settings.constants.S3_TARGET_CONTABO:
            self.upload_to_bucket_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET,
            key,
            json.dumps(data, default=default), gzip_data=True)
        elif target==settings.constants.S3_TARGET_IDRIVEE2:
            self.upload_to_bucket_idrive2e(settings.constants.SRAVZ_DATA_S3_BUCKET,
            key,
            json.dumps(data, default=default), gzip_data=True)

    def upload_data_to_s3(self, data, bucket_name, prefix):
        self.upload_to_bucket(bucket_name,
        prefix,
        json.dumps(data, default=default), gzip_data=True)

    def upload_data_to_contabo(self, data, bucket_name, prefix, target=settings.constants.S3_TARGET_CONTABO):
        if target==settings.constants.S3_TARGET_CONTABO:
            self.upload_to_bucket_contabo(bucket_name,
            prefix,
            json.dumps(data, default=default), gzip_data=True)
        elif target==settings.constants.S3_TARGET_IDRIVEE2:
            self.upload_to_bucket_idrive2e(bucket_name,
            prefix,
            json.dumps(data, default=default), gzip_data=True)
                
    def download_quotes_from_s3(self, collection_name):
        try:
            return json.loads(self.download_object(settings.constants.SRAVZ_DATA_S3_BUCKET,
            f"{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{collection_name}.json",
            gzip_data = True), object_hook=object_hook)
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchKey':
                self.logger.error(f"No object found - returning empty: Bucket: {settings.constants.SRAVZ_DATA_S3_BUCKET} Key: {settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{collection_name}.json")
                return None
            else:
                raise

    def download_quotes_from_contabo(self, collection_name, target=settings.constants.S3_TARGET_CONTABO):
        try:
            if target==settings.constants.S3_TARGET_CONTABO:
                return json.loads(self.download_object_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET,
                f"{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{collection_name}.json",
                gzip_data = True), object_hook=object_hook)
            elif target==settings.constants.S3_TARGET_IDRIVEE2:
                return json.loads(self.download_object_idrivee2(settings.constants.SRAVZ_DATA_S3_BUCKET,
                f"{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{collection_name}.json",
                gzip_data = True), object_hook=object_hook)
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchKey':
                self.logger.error(f"No object found - returning empty: Bucket: {settings.constants.SRAVZ_DATA_S3_BUCKET} Key: {settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{collection_name}.json")
                return None
            else:
                raise

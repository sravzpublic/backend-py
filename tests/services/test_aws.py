from src.util import logger
from src.services import aws
from src.util import settings
import json
# from dask.distributed import Client

LOGGER = logger.RotatingLogger(__name__).getLogger()

def test_is_quote_updated_today_s3():
    awse = aws.engine()
    status = awse.is_quote_updated_today('stk_us_aapl')
    assert status in [True, False]

def test_is_quote_updated_today_contabo():
    awse = aws.engine()
    status = awse.is_quote_updated_today('stk_us_aapl', provider='contabo')
    assert status in [True, False]

def test_is_quote_updated_today_s3_invalid_ticker():
    awse = aws.engine()
    status = awse.is_quote_updated_today('invalid')
    assert status is False

def test_is_quote_updated_today_contabo_invalid_ticker():
    awse = aws.engine()
    status = awse.is_quote_updated_today('invalid', provider='contabo')
    assert status is False

def test_upload_to_bucket_idrive2e():
    awse = aws.engine()
    awse.upload_to_bucket_idrive2e('sravz-data', 'test', "testdata")

def test_download_object_idrivee2():
    awse = aws.engine()
    data = awse.download_object_idrivee2('sravz-data', 'test', gzip_data=True)
    assert data == "testdata"

def test_upload_download_object_to_bucket_contabo():
    awse = aws.engine()
    awse.upload_to_bucket_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, 'test', json.dumps(['a', 'b', 'c']))
    data = awse.download_object_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, 'test', gzip_data=True)
    assert json.loads(data) == ['a', 'b', 'c']

def test_upload_file_to_contabo():
    awse = aws.engine()
    new_file = open("/tmp/test.test", "w")
    new_file.write('test data')
    new_file.close()
    data = awse.upload_file_to_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, 
                                       'test.test', '/tmp/test.test', 
                                       target=settings.constants.S3_TARGET_CONTABO)
    
def test_upload_file_to_contabo_idrivee2():
    awse = aws.engine()
    new_file = open("/tmp/test.test", "w")
    new_file.write('test data')
    new_file.close()
    data = awse.upload_file_to_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, 
                                       'test.test', '/tmp/test.test', 
                                       target=settings.constants.S3_TARGET_IDRIVEE2)
    assert data is None

def test_is_quote_updated_today_idrivee2_invalid_key():
    awse = aws.engine()
    status = awse.is_quote_updated_today('invalid', provider=settings.constants.S3_TARGET_IDRIVEE2)
    assert status is False    

def test_is_quote_updated_today_idrivee2_valid_key():
    awse = aws.engine()
    new_file = open("/tmp/test.test.json", "w")
    new_file.write('test data')
    new_file.close()
    awse.upload_file_to_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, 
                                       'historical/test.test.json', '/tmp/test.test.json', 
                                       target=settings.constants.S3_TARGET_IDRIVEE2)    
    status = awse.is_quote_updated_today('test.test', provider=settings.constants.S3_TARGET_IDRIVEE2)
    assert status is True        

def test_download_object_idrivee2():
    awse = aws.engine()
    awse.upload_quotes_to_contabo( "hello world", "test", target=settings.constants.S3_TARGET_IDRIVEE2)
    data = awse.download_object_idrivee2('sravz-data', 'historical/test.json', gzip_data=True)
    assert data == '"hello world"'     

def test_upload_data_to_contabo():
    awse = aws.engine()
    awse.upload_data_to_contabo(['Hello World'], 'sravz-data', 'test1.json', target=settings.constants.S3_TARGET_IDRIVEE2)
    data = awse.download_object_idrivee2('sravz-data', 'test1.json', gzip_data=True)
    assert json.loads(data) == ['Hello World']    

def test_download_quotes_from_contabo():
    awse = aws.engine()
    awse.upload_quotes_to_contabo( "hello world", "test", target=settings.constants.S3_TARGET_IDRIVEE2)
    data = awse.download_quotes_from_contabo('test', target=settings.constants.S3_TARGET_IDRIVEE2)
    assert data == "hello world"  

def test_upload_quotes_to_contabo():
    awse = aws.engine()
    awse.upload_quotes_to_contabo( "hello world", "test", target=settings.constants.S3_TARGET_CONTABO)
    data = awse.download_quotes_from_contabo('test', target=settings.constants.S3_TARGET_CONTABO)
    assert data == "hello world"  

def test_upload_quotes_to_contabo_with_prefix():
    awse = aws.engine()
    awse.upload_quotes_to_contabo("hello world",
                                  "", 
                                  prefix="test",
                                  target=settings.constants.S3_TARGET_CONTABO)
    data = awse.download_quotes_from_contabo('test', 
                                             target=settings.constants.S3_TARGET_CONTABO)
    assert data == "hello world"  

def test_upload_quotes_to_aws():
    awse = aws.engine()
    awse.upload_quotes_to_s3( "hello world", "test")
    data = awse.download_quotes_from_s3('test')
    assert data == "hello world"  

def test_upload_quotes_to_idrivee2():
    awse = aws.engine()
    awse.upload_quotes_to_contabo( "hello world", "test", target=settings.constants.S3_TARGET_IDRIVEE2)
    data = awse.download_quotes_from_contabo('test', target=settings.constants.S3_TARGET_IDRIVEE2)
    assert data == "hello world"   
    
def test_is_quote_updated_today_contabo():
    awse = aws.engine()
    awse.upload_quotes_to_contabo( "hello world", "test", target=settings.constants.S3_TARGET_CONTABO)
    status = awse.is_quote_updated_today('test', provider=settings.constants.S3_TARGET_CONTABO)
    assert status is True

def test_is_file_uploaded_today():
    awse = aws.engine()
    # awse.delete_from_bucket_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, "test")
    awse.upload_to_bucket_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, "test", "hello world")
    status = awse.is_file_uploaded_today(settings.constants.SRAVZ_DATA_S3_BUCKET, 
                                         'test', 
                                         provider=settings.constants.S3_TARGET_CONTABO)
    assert status is True    

def test_is_file_uploaded_n_days_back():
    awse = aws.engine()
    awse.upload_to_bucket_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, "test", "hello world")
    status = awse.is_file_uploaded_n_days_back(settings.constants.SRAVZ_DATA_S3_BUCKET,
                                               'test', 
                                               0,
                                               provider=settings.constants.S3_TARGET_CONTABO)
    assert status is True        

def test_download_file_from_s3():
    awse = aws.engine()
    new_file = open("/tmp/test.test", "w")
    new_file.write('test data')
    new_file.close()
    awse.upload_file_to_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, 
                                'test.test', '/tmp/test.test', 
                                target=settings.constants.S3_TARGET_CONTABO)
    awse.download_file_from_s3(settings.constants.SRAVZ_DATA_S3_BUCKET, 
                            'test.test', '/tmp/test_downloaded.test', 
                            target=settings.constants.S3_TARGET_CONTABO)
    with open('/tmp/test_downloaded.test', 'r') as f:
        data = f.read()
    assert data == 'test data'
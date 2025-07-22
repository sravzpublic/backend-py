'''
    Calculates YTD performance for the US stocks
'''
import pandas as pd
import datetime as DT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
# from dask.distributed import Client
from io import StringIO
import sys,os
sys.path.append(os.path.realpath(f"{os.path.dirname(os.path.abspath(__file__))}/../.."))
sys.path.append("/home/ubuntu/")
from src.util import settings, logger
from src.services import mdb, aws
import awswrangler as wr

_logger = logger.RotatingLogger(__name__).getLogger()
awse = aws.engine()

def get_last_friday(from_date):
    closest_friday = from_date + timedelta(days=(4 - from_date.weekday()))
    return (closest_friday if closest_friday < from_date
            else closest_friday - timedelta(days=7))

def process_date(data_and_name_to_process):
    data_to_process, name = data_and_name_to_process
    # url = "https://people.sc.fsu.edu/~jburkardt/data/csv/trees.csv"
    # return pd.DataFrame({'num_legs': [2, 4, 8, 0], 'num_wings': [2, 0, 0, 0], 'num_specimen_seen': [10, 2, 1, 8]}, index=['falcon', 'dog', 'spider', 'fish'])
    # df = pd.read_csv(url)
    # url = "https://eodhistoricaldata.com/api/eod/{0}.BOND?api_token={1}&order=d&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY)
    url = f"https://eodhistoricaldata.com/api/eod-bulk-last-day/US?api_token={settings.constants.EODHISTORICALDATA_API_KEY}&date={data_to_process.strftime('%Y-%m-%d')}"
    # _logger.info("Processing url %s: " % (url))
    df = pd.read_csv(url)
    # TESTDATA = StringIO("""Code,Ex,Date,Open,High,Low,Close,Adjusted_close,Volume
    # A,US,2021-10-13,149.08,150.88,148.74,150.22,150.22,1332995
    # AA,US,2021-10-13,48.135,48.9,47.23,48.4,48.4,5774532
    # AAA,US,2021-10-13,25.0098,25.0098,25,25,25,103
    # AAAAX,US,2021-10-13,12.72,12.72,12.72,12.72,12.72,0
    # """)
    # df = pd.read_csv(TESTDATA, sep=",")
    df = df.set_index(['Code', 'Ex'])
    df = df[~df.index.duplicated(keep='first')]
    df = df.add_suffix(f"_{name}")
    return df
    # return data_to_process

def percentage(start, end):
    return round((start - end) / end * 100, 2)

def calculate_ytds(df):
    df['Adjusted_close_week_ago_return_percent'] = percentage(df['Adjusted_close_today'], df['Adjusted_close_week_ago']) # (df['Adjusted_close_today'] - df['Adjusted_close_week_ago'])/100
    df['Adjusted_close_three_months_ago_return_percent'] = percentage(df['Adjusted_close_today'], df['Adjusted_close_three_months_ago']) # (df['Adjusted_close_today'] - df['Adjusted_close_three_months_ago'])/100
    df['Adjusted_close_six_months_ago_return_percent'] = percentage(df['Adjusted_close_today'], df['Adjusted_close_six_months_ago']) # (df['Adjusted_close_today'] - df['Adjusted_close_six_months_ago'])/100
    df['Adjusted_close_year_start_date_return_percent'] = percentage(df['Adjusted_close_today'], df['Adjusted_close_year_start_date']) # (df['Adjusted_close_today'] - df['Adjusted_close_year_start_date'])/100
    df['Adjusted_close_one_year_ago_return_percent'] = percentage(df['Adjusted_close_today'], df['Adjusted_close_one_year_ago']) # (df['Adjusted_close_today'] - df['Adjusted_close_one_year_ago'])/100
    df['Adjusted_close_three_years_ago_return_percent'] = percentage(df['Adjusted_close_today'], df['Adjusted_close_three_years_ago']) # (df['Adjusted_close_today'] - df['Adjusted_close_three_years_ago'])/100
    df['Adjusted_close_five_years_ago_return_percent'] = percentage(df['Adjusted_close_today'], df['Adjusted_close_five_years_ago']) # (df['Adjusted_close_today'] - df['Adjusted_close_five_years_ago'])/100
    df['Adjusted_close_ten_years_ago_return_percent'] = percentage(df['Adjusted_close_today'], df['Adjusted_close_ten_years_ago']) # (df['Adjusted_close_today'] - df['Adjusted_close_ten_years_ago'])/100
    return df

def convert_date_column_format(df):
    for column in ["today", "week_ago", "three_months_ago", "six_months_ago", "year_start_date", "one_year_ago", "three_years_ago", "five_years_ago", "ten_years_ago"]:
        df[f'Date_{column}'] = df[f'Date_{column}'].dt.strftime('%Y-%m-%d')
    return df

def get_seed_ticker_historical_data():
        url = "https://eodhistoricaldata.com/api/eod/{0}.US?api_token={1}&order=d&fmt=json".format('AMZN', settings.constants.EODHISTORICALDATA_API_KEY)
        df = pd.read_json(url)
        return df

def upload_ytd_df_to_aws(df):
    # data = df.assign( **df.select_dtypes(['datetime']).astype(str).to_dict('list')).to_dict('record')
    # awse.upload_quotes_to_s3(data, 'ytd_us')
    # return df
    df.reset_index(level=0, inplace=True)
    path = f"s3://{settings.constants.SRAVZ_DATA_S3_BUCKET}/{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/ytd_us.parquet"
    wr.s3.to_parquet(df, path)
    df_codes = df["Code"]
    df_codes = df_codes.drop_duplicates()
    path = f"s3://{settings.constants.SRAVZ_DATA_S3_BUCKET}/{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/ytd_codes.json"
    wr.s3.to_json(df_codes, path, orient='split', index=False)
    return f"Uploaded {len(df)} records to s3 in parquet format at {path}"

def upload_quotes_to_db(df):
    mdbe = mdb.engine()
    df.reset_index(level=0, inplace=True)
    data = df.assign( **df.select_dtypes(['datetime']).astype(str).to_dict('list')).to_dict('record')
    print(data[0])
    mdbe.upsert_to_collection(settings.constants.YTD_US_COLLECTDION, data, upsert_clause_field = 'Code')
    mdbe.create_index_collection(settings.constants.YTD_US_COLLECTDION, "Code")
    return f"Upserted {len(data)} records to db"

def get_ytd_data():
    # seed_amazon_df = df.loc[0]['date'].date()
    # client = Client(f'{settings.constants.DASK_SCHEDULER_HOST_NAME}:8786')
    _logger.info(f"Connected to Dask Scheduler at {settings.constants.DASK_SCHEDULER_HOST_NAME}")
    df = get_seed_ticker_historical_data()
    current_date = df.loc[0]['date'].date() # get_last_friday(datetime.now()).date()
    week_ago = df.loc[5]['date'].date() # get_last_friday(current_date + relativedelta(weeks=-1))
    three_months_ago = df.loc[20*3]['date'].date() # get_last_friday(current_date + relativedelta(months=-3))
    six_months_ago = df.loc[20*6]['date'].date() # get_last_friday(current_date + relativedelta(months=-6))
    year_start_date = df[df['date'].dt.year == df.loc[0]['date'].year]['date'].min().date() # get_last_friday(datetime.now().date().replace(month=1, day=2))
    one_year_ago = df.loc[250]['date'].date() # get_last_friday(current_date + relativedelta(years=-1))
    three_years_ago = df.loc[250*3]['date'].date() # get_last_friday(current_date + relativedelta(years=-3))
    five_years_ago = df.loc[250*5]['date'].date() # get_last_friday(current_date + relativedelta(years=-5))
    ten_years_ago = df.loc[250*10]['date'].date() # get_last_friday(current_date + relativedelta(years=-10))
    dates_to_process = [(current_date, "today"), (week_ago, "week_ago"), (three_months_ago, "three_months_ago"), (six_months_ago, "six_months_ago"), (year_start_date, "year_start_date"), (one_year_ago, "one_year_ago"), (three_years_ago, "three_years_ago"), (five_years_ago, "five_years_ago"), (ten_years_ago, "ten_years_ago")]
    _logger.info("Dates to process: %s" % (dates_to_process))
    # future = client.map(process_date, dates_to_process)
    # df_all = pd.concat(client.gather(future), axis=1)
    df_all = pd.concat([process_date(x) for x in dates_to_process], axis=1)
    #future = client.map(calculate_ytds, [df_all])
    #df_ytd = client.gather(future)
    df_ytd = calculate_ytds(df_all)
    #future = client.map(upload_ytd_df_to_aws, df_ytd)
    #status = client.gather(future)
    status = upload_ytd_df_to_aws(df_ytd)
    _logger.info(status)


if __name__ == '__main__':
    # print(get_seed_ticker())
    get_ytd_data()

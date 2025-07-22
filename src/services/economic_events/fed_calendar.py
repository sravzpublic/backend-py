'''
    Uploads fed calendar to contabo
'''
from src.util import helper, logger, settings
import datetime
import copy
import json
import requests


LOGGER = logger.RotatingLogger(__name__).getLogger()


@helper.save_data_to_contabo
@helper.empty_cache
def upload_calendar_to_contabo(upload_to_s3 = True):
    url = "https://www.federalreserve.gov/json/calendar.json"
    r = requests.get(url)
    decoded_data=r.text.encode().decode('utf-8-sig')
    data = json.loads(decoded_data)
    data_with_dates = []
    for event in data['events']:
        try:
            days = event['days'].split(",")
            for day in days:
                if event['time']:
                    event['date'] = f"{event['month'].split('-')[0].strip()}-{event['month'].split('-')[1].strip()}-{day.strip()} {event['time'].strip().replace('.' , '').upper()}" # '2009-11-29 03:17 PM'
                    event['date'] = datetime.datetime.strptime(event['date'], '%Y-%m-%d %H:%M %p').strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    event['date'] = f"{event['month'].split('-')[0].strip()}-{event['month'].split('-')[1].strip()}-{day.strip()}" # '2009-11-29'
                    event['date'] = datetime.datetime.strptime(event['date'], '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%SZ')
                data_with_dates.append(copy.deepcopy(event))
        except Exception:
            LOGGER.exception(f"Could not process event - {event}")
    LOGGER.info(f"Number of events: {len(data_with_dates)}")
    fifteen_days_back = datetime.datetime.today() - datetime.timedelta(days=15) #n=1
    fifteen_days_forward = datetime.datetime.today() + datetime.timedelta(days=15) #n=1
    data_with_dates_30_days = filter(lambda event: datetime.datetime.strptime(event['date'], '%Y-%m-%dT%H:%M:%SZ') >= fifteen_days_back
    and datetime.datetime.strptime(event['date'], '%Y-%m-%dT%H:%M:%SZ') <= fifteen_days_forward, data_with_dates)
    data_with_dates_30_days_sorted = sorted(data_with_dates_30_days, key=lambda d: d['date'], reverse=True)
    data['events'] = data_with_dates_30_days_sorted
    data['announcement'] = {}
    LOGGER.warning(f"Number of events within 15 days before and after: {len(data_with_dates_30_days_sorted)}. To be uploaded")
    LOGGER.warning(f"This is data: {data['events'][0]}")
    data = json.dumps(data)
    if upload_to_s3:
        return [data, f'{settings.constants.CONTABO_BUCKET_PREFIX}/assets/calendar.json.gz'], {'gzip_data':True}
    return [data, ''], {} 

if __name__ == '__main__':
    upload_calendar_to_contabo()


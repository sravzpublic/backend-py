import requests
import boto3
client = boto3.client(
    'ses',
    region_name='us-east-1',
)

urls = ["https://sravz.com", 
        "http://contabo1.sravz.com",
        "http://contabo2.sravz.com",
        "http://contabo3.sravz.com",
        "http://contabo4.sravz.com",
        "http://contabo5.sravz.com",
        "http://hetz1.sravz.com",
        "http://hetz2.sravz.com",
        "http://hetz3.sravz.com"
]

message_body = ""

for url in urls:
    print(f"Processing {url}")
    request_response = requests.head(url, verify=False)
    status_code = request_response.status_code
    if status_code in [200, 308]:
        print(f"{url} {status_code} is up")
    else:
        print(f"{url} {status_code} is down")        
        message_body = message_body + f"{url} {status_code} is down\n"

if message_body:
    response = client.send_email(
        Destination={
            'ToAddresses': ['sampat.ponnaganti@sravz.com'],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': message_body,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'Sravz Servers Down',
            },
        },
        Source='sampat.ponnaganti@sravz.com',
    )        

import os, google
from google.cloud import pubsub
from src.util import settings, logger

def main():
    subscriber = pubsub.SubscriberClient()
    _logger = logger.RotatingLogger(__name__).getLogger()
    project_id = 'sravztest1'
    topic = 'bucket-sravz-assets'
    sub = 'bucket-sravz-assets-sub'

    topic_name = 'projects/{0}/topics/{1}'.format(project_id, topic)
    
    subscription_name = 'projects/{0}/subscriptions/{1}'.format( project_id, sub)

    try: 
        subscriber.create_subscription(
            name=subscription_name, topic=topic_name)
    except google.api_core.exceptions.AlreadyExists:
        print("Subscription: {0} already exists".format(subscription_name))
        
    def callback(message):
        print(message.data)
        message.ack()

    subscription = subscriber.subscribe(subscription_name, callback)

    try:
        subscription.result()
    except KeyboardInterrupt:
        subscription.cancel()


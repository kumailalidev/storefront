from time import sleep
from celery import shared_task
from storefront.celery import celery


@shared_task  # RECOMMENDED APPROACH
def notify_customers(message):
    print("Sending 10k emails...")
    print(message)
    sleep(10)
    print("Emails were successfully sent!")

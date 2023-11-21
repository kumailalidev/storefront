from time import sleep
from celery import shared_task
from storefront.celery import (
    celery,
)  # import Celery instance created instance storefront project folder


# NOTE: decorating task with celery.task decorator is not recommended
# because it makes the playground dependent upon storefront project
# therefore playground will not be independent app.
# @celery.task (NOT RECOMMENDED)


@shared_task  # RECOMMENDED APPROACH
def notify_customers(message):
    print("Sending 10k emails...")
    print(message)
    sleep(10)
    print("Emails were successfully sent!")

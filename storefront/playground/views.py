from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework.views import APIView

from .tasks import notify_customers

import requests
import logging

logger = logging.getLogger(__name__)  # playground.views


class HelloView(APIView):
    # @method_decorator(cache_page(5 * 60))
    def get(self, request):
        # perform celery task
        # notify_customers.delay("Hello")

        try:
            logger.info("Calling httpbin")
            response = requests.get("https://httpbin.org/delay/2")
            logger.info("Received the response")
            data = response.json()
        except requests.ConnectionError:
            logger.critical("httpbin is offline")

        return render(request, "hello.html", {"name": "Kumail"})

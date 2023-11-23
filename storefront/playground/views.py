from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework.views import APIView

from .tasks import notify_customers

import requests


class HelloView(APIView):
    @method_decorator(cache_page(5 * 60))
    def get(self, request):
        # perform celery task
        # notify_customers.delay("Hello")

        # Simulating a slow api request, response will be send after 2 seconds of delay
        response = requests.get("https://httpbin.org/delay/2")
        data = response.json()

        return render(request, "hello.html", {"name": data})

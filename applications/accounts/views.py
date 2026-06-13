from typing import Any, Dict

import requests
from django.views.generic import TemplateView


# Helper function to extract IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')

def get_coordinates(ip) -> Dict[str, Any]:
    response = requests.get(f"https://ipwho.is/{ip}")
    if response.status_code != 200:
        return {}
    data = response.json()
    if str(ip) in {"0.0.0.0", "127.0.0.1", "localhost"}:
        return {}
    return 	{	
            "ip": ip,
    "latitude": data["latitude"],
    "longitude": data["longitude"],
    "city": data["city"],
    "region": data["region"],
    "country": data["country"]
    }
class Dashboard(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        ip = get_client_ip(self.request)
        context["coordinates"] = get_coordinates(ip)
        print(context)
        return context
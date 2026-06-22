from typing import Any, Dict

from django.views.generic import TemplateView

from common.helpers.forecast import WeatherMan
from forms.enrollment import EnrollmentIntakeForm

# Helper function to extract IP


class Dashboard(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["weather"] = WeatherMan.forecast(self.request)
        context["form"] = EnrollmentIntakeForm()
        print(context)
        return context

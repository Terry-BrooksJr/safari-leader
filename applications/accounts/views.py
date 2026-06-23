from typing import Any, Dict

from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from common.helpers.forecast import WeatherMan
from forms.enrollment import EnrollmentIntakeForm


class Dashboard(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["weather"] = WeatherMan.forecast(self.request)
        context["form"] = EnrollmentIntakeForm()
        return context


class EnrollmentIntakeView(View):
    """Process the enrollment intake form submitted over AJAX.

    The dashboard modal posts the form here with fetch() and expects JSON back
    in every case: a payload with the new child's name and detail URL on
    success, or the form's field errors (HTTP 400) so the modal can highlight
    the offending inputs without a full page reload.
    """

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        form = EnrollmentIntakeForm(request.POST)

        if not form.is_valid():
            return JsonResponse(
                {"success": False, "errors": form.errors.get_json_data()},
                status=400,
            )

        result = form.save()
        child = result["child"]

        return JsonResponse(
            {
                "success": True,
                "child_name": f"{child.first_name} {child.last_name}",
                "child_detail_url": reverse("child-detail", args=[child.pk]),
            }
        )

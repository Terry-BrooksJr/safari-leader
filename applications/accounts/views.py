from django.shortcuts import render
from django.views.generic import TemplateView
from applications.communication.models import Notification, Announcement
# Create your views here.


class Dashboard(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["notifications"] = Notification.objects.filter(user=request.user.id)
        context["announcements"] = Announcement.objects.all()
        return self.render_to_response(context)
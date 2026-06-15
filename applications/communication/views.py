from django.views.generic import DetailView, ListView

from .models import Announcement, Message, Notification


class AnnouncementsList(ListView):
    model = Announcement
    template_name = "communication/announcement_list.html"
    paginate_by = 25


class NotificationsList(ListView):
    model = Notification
    template_name = "communication/notification_list.html"
    paginate_by = 25


class AnnouncementDetails(DetailView):
    model = Announcement
    template_name = "communication/announcement_detail.html"
    context_object_name = "announcement"


class NotificationDetails(DetailView):
    model = Notification
    template_name = "communication/notification_detail.html"
    context_object_name = "notification"


class MessageDetails(DetailView):
    model = Message
    template_name = "communication/message_detail.html"
    context_object_name = "message"

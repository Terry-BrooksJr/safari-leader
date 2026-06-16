from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
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
    context_object_name = "notification"

    def get_queryset(self) -> QuerySet:
        return Notification.objects.filter(user=self.request.user).all()


class MessageList(ListView):
    model = Message
    template_name = "communication/message_list.html"
    paginate_by = 25
    context_object_name = "message"

    def get_queryset(self) -> QuerySet:
        queryset = Message.objects.filter(recipient=self.request.user).select_related(
            "recipient", "sender"
        )
        is_read = self.request.GET.get("read")
        if is_read == "true":
            queryset = queryset.filter(is_read=True)
        elif is_read == "false":
            queryset = queryset.filter(is_read=False)
        return queryset.order_by("-created_at")


class AnnouncementDetails(DetailView):
    model = Announcement
    template_name = "communication/announcement_detail.html"
    context_object_name = "announcement"


class NotificationDetails(DetailView):
    model = Notification
    template_name = "communication/notification_detail.html"
    context_object_name = "notification"


class MessageDetails(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "communication/message_detail.html"
    context_object_name = "message"


def mark_read():
    pass

from applications.communication.models import Announcement, Message, Notification


def messaging_context(request):
    context = {"announcements": Announcement.objects.all().order_by("-updated_at")}
    if request.user.is_authenticated:
        context["notifications"] = Notification.objects.filter(
            user=request.user, is_read=False
        ).order_by("-created_at")
        context["messages"] = Message.objects.filter(
            recipient=request.user, is_read=False
        ).order_by("-created_at")
    return context

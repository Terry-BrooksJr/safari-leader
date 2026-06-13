from applications.communication.models import Announcement, Notification


def messaging_context(request):
    context = {"announcements": Announcement.objects.all()}
    if request.user.is_authenticated:
        context["notifications"] = Notification.objects.filter(
            user=request.user, is_read=False
        )
    return context

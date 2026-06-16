from django.urls import path

from applications.communication.views import (
    AnnouncementDetails,
    AnnouncementsList,
    MessageDetails,
    MessageList,
    NotificationDetails,
    NotificationsList,
)

urlpatterns = [
    path("message/<int:pk>", MessageDetails.as_view(), name="message-detail"),
    path(
        "notification/<int:pk>",
        NotificationDetails.as_view(),
        name="notifications-detail",
    ),
    path(
        "annoucement/<int:pk>",
        AnnouncementDetails.as_view(),
        name="announcement-detail",
    ),
    path("messages/", MessageList.as_view(), name="message-list"),
    path("notifications/", NotificationsList.as_view(), name="notification-list"),
    path("announcements/", AnnouncementsList.as_view(), name="announcement-list"),
]

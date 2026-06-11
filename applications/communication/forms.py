from crispy_forms.helper import FormHelper
from django.forms import ModelForm
from django.urls import reverse

from .models import Announcement, Notification


class AnnouncementForm(ModelForm):
    class Meta:
        """Meta definition for AnnouncementForm."""

        model = Announcement
        fields = ["title", "message", "sites"]
        labels = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse("create-announcement")
        self.helper.form_id = "announcement"
        self.helper.form_method = "post"

class NotificationForm(ModelForm):
    class Meta:
        """Meta definition for NotificationForm."""

        model = Notification
        fields = ["user", "type", "message", "is_read"]
        labels = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse("create-notifications")
        self.helper.form_id = "notification"
        self.helper.form_method = "post"

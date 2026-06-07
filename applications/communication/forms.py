from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Reset, Row, Submit
from django.forms import BooleanField, CheckboxInput, ModelForm, fields
from django.forms.widgets import DateInput
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Announcement, Notification

class AnnouncementForm(ModelForm):
    pass

    class Meta:
        """Meta definition for AnnouncementForm."""

        model = Announcement
        exclude = ["created_by"]
        labels = {}
            
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse("create-annoucement")
        self.helper.form_id = "announcement"
        self.helper.form_method = "post"
        self.helper.layout = Layout()
        
class NotificationForm(ModelForm):
    pass


    class Meta:
        """Meta definition for NotificationForm."""

        model = Notification
        exclude = ["created_by", "updated_at"]
        labels = {}
            
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse("create-notifications")
        self.helper.form_id = "notification"
        self.helper.form_method = "post"
        self.helper.layout = Layout()
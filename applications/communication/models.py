from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from applications.facilities.models import Site
from applications.staffing.models import StaffProfile


class NOTIFICATION_TYPE(models.TextChoices):
    REG = "R", _("Regular")
    URGENT = "U", _("Urgent")
    COMPLIANCE = "C", _("Compliance")
    HR = "HR", _("Human Resources")
    TECH = "T", _("Technical")
    OTHER = "O", _("Other")


class Announcement(models.Model):
    title = models.CharField(max_length=120)
    message = models.TextField()
    created_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements_created",
    )
    sites = models.ManyToManyField(
        Site,
        related_name="announcements",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4(), 
        editable=False
    )
    recipient = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    sender = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        related_name="sent_messages",
        null=True,
        blank=True,
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        recipient = self.get_reciever_username()
        sender = self.get_sender_username()
        return f"{sender} -> {recipient} at ({self.created_at})"

    def mark_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])

    def mark_unread(self):
        self.is_read = False
        self.save(update_fields=["is_read"])

    def get_reciever_username(self) -> str:
        return self.recipient.username if self.recipient is not None else "Deleted User"

    def get_sender_username(self) -> str:
        return self.sender.username if self.sender is not None else "Deleted User"


class Notification(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
    )
    type = models.CharField(max_length=25, choices=NOTIFICATION_TYPE.choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.get_username() if self.user_id else "Deleted User"
        return f"{username} - {self.type} ({self.created_at})"

    def mark_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])

    def mark_unread(self):
        self.is_read = False
        self.save(update_fields=["is_read"])

    def get_username(self) -> str:
        return self.user.username if self.user is not None else "Deleted User"

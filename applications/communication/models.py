from django.db import models
from applications.staffing.models import StaffProfile
from applications.facilities.models import Site
from django.utils.translation import gettext_lazy as _


class NOTIFICATION_TYPE(models.TextChoices):
    REG = 'R', _("Regular")
    URGENT = 'U', _("Urgent")
    COMPLIANCE = 'C', _("Compliance")
    HR = 'HR', _("Human Resources")
    TECH = 'T', _("Technical")
    OTHER = 'O', _("Other")
    
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
    
class Notification(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=25, choices=NOTIFICATION_TYPE.choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        username = self.user.get_username() if self.user_id else "unknown_user"
        return f"{username} - {self.type} ({self.created_at})"

    def mark_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])

    def mark_unread(self):
        self.is_read = False
        self.save(update_fields=["is_read"])
        
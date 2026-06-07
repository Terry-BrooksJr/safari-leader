from datetime import datetime
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from applications.communication.forms import AnnouncementForm, NotificationForm
from applications.communication.models import Announcement, Notification
from applications.communication.views import (
    AnnouncementDetails,
    AnnouncementsList,
    NotificationDetails,
    NotificationsList,
)


# ─── Model Tests ───────────────────────────────────────────────────────────────


class NotificationStrTest(SimpleTestCase):
    """Verify Notification.__str__ uses username, not user.id."""

    def test_str_with_valid_user(self):
        mock_notif = Mock()
        mock_notif.user.get_username.return_value = "jdoe"
        mock_notif.user_id = 1
        mock_notif.type = "R"
        mock_notif.created_at = datetime(2024, 6, 15, 10, 30)
        result = Notification.__str__(mock_notif)
        self.assertIn("jdoe", result)
        self.assertIn("R", result)

    def test_str_does_not_use_user_id(self):
        """Regression: previously returned user.id in the string."""
        mock_notif = Mock()
        mock_notif.user.get_username.return_value = "jdoe"
        mock_notif.user_id = 42
        mock_notif.type = "R"
        mock_notif.created_at = datetime(2024, 6, 15)
        result = Notification.__str__(mock_notif)
        self.assertNotIn("42 -", result)

    def test_str_with_null_user_id(self):
        mock_notif = Mock()
        mock_notif.user_id = None
        mock_notif.type = "U"
        mock_notif.created_at = datetime(2024, 6, 15)
        result = Notification.__str__(mock_notif)
        self.assertIn("unknown_user", result)
        self.assertIn("U", result)

    def test_str_with_zero_user_id(self):
        mock_notif = Mock()
        mock_notif.user_id = 0
        mock_notif.type = "C"
        mock_notif.created_at = datetime(2024, 1, 1)
        result = Notification.__str__(mock_notif)
        self.assertIn("unknown_user", result)


class NotificationMarkReadTest(SimpleTestCase):
    """Verify mark_read sets is_read=True and uses update_fields."""

    def test_mark_read_sets_flag(self):
        mock_notif = Mock()
        mock_notif.is_read = False
        Notification.mark_read(mock_notif)
        self.assertTrue(mock_notif.is_read)

    def test_mark_read_calls_save_with_update_fields(self):
        mock_notif = Mock()
        mock_notif.is_read = False
        Notification.mark_read(mock_notif)
        mock_notif.save.assert_called_once_with(update_fields=["is_read"])


class NotificationMarkUnreadTest(SimpleTestCase):
    """Verify mark_unread sets is_read=False and uses update_fields."""

    def test_mark_unread_clears_flag(self):
        mock_notif = Mock()
        mock_notif.is_read = True
        Notification.mark_unread(mock_notif)
        self.assertFalse(mock_notif.is_read)

    def test_mark_unread_calls_save_with_update_fields(self):
        mock_notif = Mock()
        mock_notif.is_read = True
        Notification.mark_unread(mock_notif)
        mock_notif.save.assert_called_once_with(update_fields=["is_read"])


# ─── Form Tests ────────────────────────────────────────────────────────────────


class AnnouncementFormMetaTest(SimpleTestCase):
    """Verify AnnouncementForm uses explicit fields (not exclude)."""

    def test_fields_are_explicit(self):
        self.assertEqual(
            AnnouncementForm.Meta.fields, ["title", "message", "sites"]
        )

    def test_no_exclude_attribute(self):
        self.assertFalse(hasattr(AnnouncementForm.Meta, "exclude"))

    def test_model_is_announcement(self):
        self.assertEqual(AnnouncementForm.Meta.model, Announcement)


class NotificationFormMetaTest(SimpleTestCase):
    """Verify NotificationForm uses explicit fields (not exclude)."""

    def test_fields_are_explicit(self):
        self.assertEqual(
            NotificationForm.Meta.fields, ["user", "type", "message", "is_read"]
        )

    def test_no_exclude_attribute(self):
        self.assertFalse(hasattr(NotificationForm.Meta, "exclude"))

    def test_model_is_notification(self):
        self.assertEqual(NotificationForm.Meta.model, Notification)


# ─── View Tests ────────────────────────────────────────────────────────────────


class AnnouncementsListViewConfigTest(SimpleTestCase):
    """Verify AnnouncementsList is a functional ListView (not an empty stub)."""

    def test_model_is_announcement(self):
        self.assertEqual(AnnouncementsList.model, Announcement)

    def test_template_name(self):
        self.assertEqual(
            AnnouncementsList.template_name, "communication/announcement_list.html"
        )

    def test_paginate_by(self):
        self.assertEqual(AnnouncementsList.paginate_by, 25)


class NotificationsListViewConfigTest(SimpleTestCase):
    """Verify NotificationsList is a functional ListView."""

    def test_model_is_notification(self):
        self.assertEqual(NotificationsList.model, Notification)

    def test_template_name(self):
        self.assertEqual(
            NotificationsList.template_name, "communication/notification_list.html"
        )

    def test_paginate_by(self):
        self.assertEqual(NotificationsList.paginate_by, 25)


class AnnouncementDetailsViewConfigTest(SimpleTestCase):
    """Verify AnnouncementDetails is a functional DetailView."""

    def test_model_is_announcement(self):
        self.assertEqual(AnnouncementDetails.model, Announcement)

    def test_template_name(self):
        self.assertEqual(
            AnnouncementDetails.template_name,
            "communication/announcement_detail.html",
        )

    def test_context_object_name(self):
        self.assertEqual(AnnouncementDetails.context_object_name, "announcement")


class NotificationDetailsViewConfigTest(SimpleTestCase):
    """Verify NotificationDetails is a functional DetailView."""

    def test_model_is_notification(self):
        self.assertEqual(NotificationDetails.model, Notification)

    def test_template_name(self):
        self.assertEqual(
            NotificationDetails.template_name,
            "communication/notification_detail.html",
        )

    def test_context_object_name(self):
        self.assertEqual(NotificationDetails.context_object_name, "notification")


class ViewClassNamingTest(SimpleTestCase):
    """Verify the misspelled class names were corrected."""

    def test_announcements_list_spelling(self):
        self.assertEqual(AnnouncementsList.__name__, "AnnouncementsList")

    def test_announcement_details_spelling(self):
        self.assertEqual(AnnouncementDetails.__name__, "AnnouncementDetails")

    def test_no_misspelled_annoucement_class(self):
        from applications.communication import views

        self.assertFalse(hasattr(views, "AnnoucementsList"))
        self.assertFalse(hasattr(views, "AnnoucementDetails"))

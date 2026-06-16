from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.utils import timezone

from applications.accounts.models import User
from applications.communication.forms import AnnouncementForm, NotificationForm
from applications.communication.models import Announcement, Message, Notification
from applications.communication.views import (
    AnnouncementDetails,
    AnnouncementsList,
    MessageDetails,
    MessageList,
    NotificationDetails,
    NotificationsList,
)

_seq = 0


def _uname(prefix):
    global _seq
    _seq += 1
    return f"{prefix}_{_seq}"


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
        self.assertIn("Deleted User", result)
        self.assertIn("U", result)

    def test_str_with_zero_user_id(self):
        mock_notif = Mock()
        mock_notif.user_id = 0
        mock_notif.type = "C"
        mock_notif.created_at = datetime(2024, 1, 1)
        result = Notification.__str__(mock_notif)
        self.assertIn("Deleted User", result)


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


class NotificationGetUsernameTest(SimpleTestCase):
    """Verify Notification.get_username falls back to 'Deleted User' on null user."""

    def test_returns_username_when_user_present(self):
        mock_notif = Mock()
        mock_notif.user.username = "jdoe"
        self.assertEqual(Notification.get_username(mock_notif), "jdoe")

    def test_returns_placeholder_when_user_is_none(self):
        mock_notif = Mock()
        mock_notif.user = None
        self.assertEqual(Notification.get_username(mock_notif), "Deleted User")


class AnnouncementStrTest(SimpleTestCase):
    """Verify Announcement.__str__ returns the title."""

    def test_str_returns_title(self):
        mock_ann = Mock()
        mock_ann.title = "Snow Day Closure"
        self.assertEqual(Announcement.__str__(mock_ann), "Snow Day Closure")


class MessageStrTest(SimpleTestCase):
    """Verify Message.__str__ formats as 'sender -> recipient at (created_at)'."""

    def _make_mock(self, sender, recipient, created_at):
        mock_msg = Mock()
        mock_msg.get_sender_username.return_value = sender
        mock_msg.get_reciever_username.return_value = recipient
        mock_msg.created_at = created_at
        return mock_msg

    def test_str_with_both_users(self):
        mock_msg = self._make_mock("alice", "bob", datetime(2024, 6, 15, 10, 30))
        result = Message.__str__(mock_msg)
        self.assertEqual(result, "alice -> bob at (2024-06-15 10:30:00)")

    def test_str_uses_username_helpers(self):
        mock_msg = self._make_mock("alice", "bob", datetime(2024, 1, 1))
        Message.__str__(mock_msg)
        mock_msg.get_sender_username.assert_called_once_with()
        mock_msg.get_reciever_username.assert_called_once_with()

    def test_str_with_deleted_sender(self):
        mock_msg = self._make_mock("Deleted User", "bob", datetime(2024, 1, 1))
        result = Message.__str__(mock_msg)
        self.assertTrue(result.startswith("Deleted User -> bob"))


class MessageMarkReadTest(SimpleTestCase):
    """Verify Message.mark_read sets is_read=True via update_fields."""

    def test_mark_read_sets_flag(self):
        mock_msg = Mock()
        mock_msg.is_read = False
        Message.mark_read(mock_msg)
        self.assertTrue(mock_msg.is_read)

    def test_mark_read_calls_save_with_update_fields(self):
        mock_msg = Mock()
        mock_msg.is_read = False
        Message.mark_read(mock_msg)
        mock_msg.save.assert_called_once_with(update_fields=["is_read"])


class MessageMarkUnreadTest(SimpleTestCase):
    """Verify Message.mark_unread sets is_read=False via update_fields."""

    def test_mark_unread_clears_flag(self):
        mock_msg = Mock()
        mock_msg.is_read = True
        Message.mark_unread(mock_msg)
        self.assertFalse(mock_msg.is_read)

    def test_mark_unread_calls_save_with_update_fields(self):
        mock_msg = Mock()
        mock_msg.is_read = True
        Message.mark_unread(mock_msg)
        mock_msg.save.assert_called_once_with(update_fields=["is_read"])


class MessageUsernameHelpersTest(SimpleTestCase):
    """Verify the receiver/sender username helpers handle deleted (null) users."""

    def test_receiver_username_present(self):
        mock_msg = Mock()
        mock_msg.recipient.username = "bob"
        self.assertEqual(Message.get_reciever_username(mock_msg), "bob")

    def test_receiver_username_when_none(self):
        mock_msg = Mock()
        mock_msg.recipient = None
        self.assertEqual(Message.get_reciever_username(mock_msg), "Deleted User")

    def test_sender_username_present(self):
        mock_msg = Mock()
        mock_msg.sender.username = "alice"
        self.assertEqual(Message.get_sender_username(mock_msg), "alice")

    def test_sender_username_when_none(self):
        mock_msg = Mock()
        mock_msg.sender = None
        self.assertEqual(Message.get_sender_username(mock_msg), "Deleted User")


# ─── Form Tests ────────────────────────────────────────────────────────────────


class AnnouncementFormMetaTest(SimpleTestCase):
    """Verify AnnouncementForm uses explicit fields (not exclude)."""

    def test_fields_are_explicit(self):
        self.assertEqual(AnnouncementForm.Meta.fields, ["title", "message", "sites"])

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


class MessageListViewConfigTest(SimpleTestCase):
    """Verify MessageList is a functional ListView."""

    def test_model_is_message(self):
        self.assertEqual(MessageList.model, Message)

    def test_template_name(self):
        self.assertEqual(MessageList.template_name, "communication/message_list.html")

    def test_paginate_by(self):
        self.assertEqual(MessageList.paginate_by, 25)

    def test_context_object_name(self):
        self.assertEqual(MessageList.context_object_name, "message")


class MessageDetailsViewConfigTest(SimpleTestCase):
    """Verify MessageDetails is a login-protected DetailView."""

    def test_model_is_message(self):
        self.assertEqual(MessageDetails.model, Message)

    def test_template_name(self):
        self.assertEqual(
            MessageDetails.template_name, "communication/message_detail.html"
        )

    def test_context_object_name(self):
        self.assertEqual(MessageDetails.context_object_name, "message")

    def test_requires_login(self):
        self.assertTrue(issubclass(MessageDetails, LoginRequiredMixin))


class MessageListGetQuerysetUnitTest(SimpleTestCase):
    """Unit-test MessageList.get_queryset branching without touching the DB."""

    def setUp(self):
        self.factory = RequestFactory()

    def _build_view(self, query_string=""):
        request = self.factory.get(f"/messages/{query_string}")
        request.user = Mock(name="request_user")
        view = MessageList()
        view.request = request
        return view

    @patch("applications.communication.views.Message")
    def test_filters_by_recipient_and_selects_related(self, mock_message):
        view = self._build_view()
        view.get_queryset()
        mock_message.objects.filter.assert_called_once_with(recipient=view.request.user)
        mock_message.objects.filter.return_value.select_related.assert_called_once_with(
            "recipient", "sender"
        )

    @patch("applications.communication.views.Message")
    def test_orders_by_created_at_descending(self, mock_message):
        base_qs = mock_message.objects.filter.return_value.select_related.return_value
        view = self._build_view()
        view.get_queryset()
        base_qs.order_by.assert_called_once_with("-created_at")

    @patch("applications.communication.views.Message")
    def test_read_true_filters_is_read_true(self, mock_message):
        base_qs = mock_message.objects.filter.return_value.select_related.return_value
        view = self._build_view("?read=true")
        view.get_queryset()
        base_qs.filter.assert_called_once_with(is_read=True)

    @patch("applications.communication.views.Message")
    def test_read_false_filters_is_read_false(self, mock_message):
        base_qs = mock_message.objects.filter.return_value.select_related.return_value
        view = self._build_view("?read=false")
        view.get_queryset()
        base_qs.filter.assert_called_once_with(is_read=False)

    @patch("applications.communication.views.Message")
    def test_no_read_param_does_not_filter_is_read(self, mock_message):
        base_qs = mock_message.objects.filter.return_value.select_related.return_value
        view = self._build_view()
        view.get_queryset()
        base_qs.filter.assert_not_called()

    @patch("applications.communication.views.Message")
    def test_unknown_read_value_is_ignored(self, mock_message):
        base_qs = mock_message.objects.filter.return_value.select_related.return_value
        view = self._build_view("?read=maybe")
        view.get_queryset()
        base_qs.filter.assert_not_called()


class NotificationsListGetQuerysetUnitTest(SimpleTestCase):
    """Unit-test NotificationsList.get_queryset filters by the request user."""

    def setUp(self):
        self.factory = RequestFactory()

    @patch("applications.communication.views.Notification")
    def test_filters_by_request_user(self, mock_notification):
        request = self.factory.get("/notifications/")
        request.user = Mock(name="request_user")
        view = NotificationsList()
        view.request = request
        view.get_queryset()
        mock_notification.objects.filter.assert_called_once_with(user=request.user)


# ─── Database-Backed Integration Tests ──────────────────────────────────────────
# These exercise the real ORM and require a test database (run in CI via Doppler).


class MessageModelPersistenceTest(TestCase):
    """Verify Message read-state helpers and username fallbacks against the DB."""

    def setUp(self):
        self.alice = User.objects.create_user(username=_uname("alice"), password="x")
        self.bob = User.objects.create_user(username=_uname("bob"), password="x")

    def test_mark_read_persists(self):
        msg = Message.objects.create(
            recipient=self.alice, sender=self.bob, message="hi"
        )
        self.assertFalse(msg.is_read)
        msg.mark_read()
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)

    def test_mark_unread_persists(self):
        msg = Message.objects.create(
            recipient=self.alice, sender=self.bob, message="hi", is_read=True
        )
        msg.mark_unread()
        msg.refresh_from_db()
        self.assertFalse(msg.is_read)

    def test_username_helpers_with_real_users(self):
        msg = Message.objects.create(
            recipient=self.alice, sender=self.bob, message="hi"
        )
        self.assertEqual(msg.get_reciever_username(), self.alice.username)
        self.assertEqual(msg.get_sender_username(), self.bob.username)

    def test_sender_username_after_sender_deleted(self):
        msg = Message.objects.create(
            recipient=self.alice, sender=self.bob, message="hi"
        )
        self.bob.delete()  # SET_NULL on sender
        msg.refresh_from_db()
        self.assertEqual(msg.get_sender_username(), "Deleted User")
        self.assertIn("Deleted User", str(msg))


class MessageListQuerysetTest(TestCase):
    """Verify MessageList.get_queryset filtering, scoping, and ordering on the DB."""

    def setUp(self):
        self.factory = RequestFactory()
        self.alice = User.objects.create_user(username=_uname("alice"), password="x")
        self.bob = User.objects.create_user(username=_uname("bob"), password="x")

        self.read_msg = Message.objects.create(
            recipient=self.alice, sender=self.bob, message="read", is_read=True
        )
        self.unread_msg = Message.objects.create(
            recipient=self.alice, sender=self.bob, message="unread", is_read=False
        )
        # Belongs to bob — must never appear in alice's queryset.
        Message.objects.create(
            recipient=self.bob, sender=self.alice, message="other", is_read=False
        )
        # Pin deterministic created_at values (auto_now_add can't be set on create).
        now = timezone.now()
        Message.objects.filter(pk=self.read_msg.pk).update(
            created_at=now - timedelta(hours=1)
        )
        Message.objects.filter(pk=self.unread_msg.pk).update(created_at=now)

    def _queryset(self, user, query_string=""):
        request = self.factory.get(f"/messages/{query_string}")
        request.user = user
        view = MessageList()
        view.request = request
        return view.get_queryset()

    def test_only_recipient_messages_returned(self):
        results = self._queryset(self.alice)
        self.assertEqual(results.count(), 2)
        self.assertTrue(all(m.recipient_id == self.alice.id for m in results))

    def test_read_true_returns_only_read(self):
        results = list(self._queryset(self.alice, "?read=true"))
        self.assertEqual([m.pk for m in results], [self.read_msg.pk])

    def test_read_false_returns_only_unread(self):
        results = list(self._queryset(self.alice, "?read=false"))
        self.assertEqual([m.pk for m in results], [self.unread_msg.pk])

    def test_ordered_newest_first(self):
        results = list(self._queryset(self.alice))
        self.assertEqual(
            [m.pk for m in results], [self.unread_msg.pk, self.read_msg.pk]
        )

    def test_other_user_sees_only_their_message(self):
        results = self._queryset(self.bob)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().recipient_id, self.bob.id)


class NotificationsListQuerysetTest(TestCase):
    """Verify NotificationsList.get_queryset scopes notifications to the user."""

    def setUp(self):
        self.factory = RequestFactory()
        self.alice = User.objects.create_user(username=_uname("alice"), password="x")
        self.bob = User.objects.create_user(username=_uname("bob"), password="x")
        Notification.objects.create(user=self.alice, type="R", message="a1")
        Notification.objects.create(user=self.alice, type="U", message="a2")
        Notification.objects.create(user=self.bob, type="R", message="b1")

    def test_returns_only_request_user_notifications(self):
        request = self.factory.get("/notifications/")
        request.user = self.alice
        view = NotificationsList()
        view.request = request
        results = view.get_queryset()
        self.assertEqual(results.count(), 2)
        self.assertTrue(all(n.user_id == self.alice.id for n in results))

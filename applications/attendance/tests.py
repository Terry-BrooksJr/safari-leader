from datetime import date, timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from applications.accounts.models import User
from applications.attendance.models import AttendanceRecord, CheckInOutEvent
from applications.children.models import AuthorizedPickupProfile, Child
from applications.handoff.models import HandoffEvent
from applications.staffing.models import StaffProfile

_seq = 0


def _uname(prefix):
    global _seq
    _seq += 1
    return f"{prefix}_{_seq}"


def _make_child(last_name="Kid"):
    return Child.objects.create(
        first_name="Test",
        last_name=last_name,
        date_of_birth=date(2022, 1, 1),
        status="A",
    )


def _make_pickup(child):
    user = User.objects.create_user(username=_uname("pickup"), password="x")
    return AuthorizedPickupProfile.objects.create(
        child=child,
        user=user,
        relationship="P",
        pickup_pin=1234,
    )


def _make_staff():
    user = User.objects.create_user(username=_uname("staff"), password="x")
    return StaffProfile.objects.create(
        user=user,
        hire_date=date(2020, 1, 1),
        personal_pin=4321,
        role_title="Instructor",
    )


class AttendanceRecordModelTest(TestCase):
    def setUp(self):
        self.child = _make_child()

    def test_one_record_per_child_per_day(self):
        AttendanceRecord.objects.create(
            child=self.child, date=date(2026, 6, 1), status="F"
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AttendanceRecord.objects.create(
                    child=self.child, date=date(2026, 6, 1), status="D"
                )

    def test_same_child_different_day_allowed(self):
        AttendanceRecord.objects.create(child=self.child, date=date(2026, 6, 1))
        AttendanceRecord.objects.create(child=self.child, date=date(2026, 6, 2))
        self.assertEqual(self.child.attendancerecord_set.count(), 2)

    def test_same_day_different_child_allowed(self):
        other = _make_child(last_name="Other")
        AttendanceRecord.objects.create(child=self.child, date=date(2026, 6, 1))
        AttendanceRecord.objects.create(child=other, date=date(2026, 6, 1))
        self.assertEqual(
            AttendanceRecord.objects.filter(date=date(2026, 6, 1)).count(), 2
        )

    def test_timeline_merges_and_orders_events_by_timestamp(self):
        record = AttendanceRecord.objects.create(
            child=self.child, date=date(2026, 6, 1), status="F"
        )
        check_in = CheckInOutEvent.objects.create(
            attendance_record=record, event_type="CI-AM"
        )
        check_out = CheckInOutEvent.objects.create(
            attendance_record=record, event_type="CO-PM"
        )
        handoff = HandoffEvent.objects.create(
            attendance_record=record,
            event_type="DO-AM",
            pickup_person=_make_pickup(self.child),
            checked_by=_make_staff(),
        )
        # auto_now timestamps are not deterministic; set them explicitly.
        base = timezone.now()
        CheckInOutEvent.objects.filter(pk=check_in.pk).update(timestamp=base)
        HandoffEvent.objects.filter(pk=handoff.pk).update(
            timestamp=base + timedelta(minutes=5)
        )
        CheckInOutEvent.objects.filter(pk=check_out.pk).update(
            timestamp=base + timedelta(hours=9)
        )

        record.refresh_from_db()
        timeline = record.timeline
        self.assertEqual(len(timeline), 3)
        self.assertEqual(
            [event.event_type for event in timeline],
            ["CI-AM", "DO-AM", "CO-PM"],
        )

    def test_str_includes_child_and_date(self):
        record = AttendanceRecord.objects.create(
            child=self.child, date=date(2026, 6, 1), status="F"
        )
        text = str(record)
        self.assertIn("Kid", text)
        self.assertIn("2026-06-01", text)


class CheckInOutEventModelTest(TestCase):
    def setUp(self):
        self.child = _make_child()
        self.record = AttendanceRecord.objects.create(
            child=self.child, date=date(2026, 6, 1), status="F"
        )

    def test_child_property_resolves_through_record(self):
        event = CheckInOutEvent.objects.create(
            attendance_record=self.record, event_type="CI-AM"
        )
        self.assertEqual(event.child, self.child)

    def test_related_name_on_record(self):
        event = CheckInOutEvent.objects.create(
            attendance_record=self.record, event_type="CI-AM"
        )
        self.assertIn(event, self.record.check_in_out_events.all())

    def test_deleting_record_cascades_to_events(self):
        event = CheckInOutEvent.objects.create(
            attendance_record=self.record, event_type="CI-AM"
        )
        self.record.delete()
        self.assertFalse(CheckInOutEvent.objects.filter(pk=event.pk).exists())

from datetime import date

from django.test import TestCase

from applications.accounts.models import User
from applications.attendance.models import AttendanceRecord
from applications.children.models import AuthorizedPickupProfile, Child
from applications.handoff.models import HandoffEvent
from applications.staffing.models import StaffProfile

_seq = 0


def _uname(prefix):
    global _seq
    _seq += 1
    return f"{prefix}_{_seq}"


class HandoffEventModelTest(TestCase):
    def setUp(self):
        self.child = Child.objects.create(
            first_name="Test",
            last_name="Kid",
            date_of_birth=date(2022, 1, 1),
            status="A",
        )
        self.record = AttendanceRecord.objects.create(
            child=self.child, date=date(2026, 6, 1), status="F"
        )
        pickup_user = User.objects.create_user(username=_uname("pickup"), password="x")
        self.pickup = AuthorizedPickupProfile.objects.create(
            child=self.child,
            user=pickup_user,
            relationship="P",
            pickup_pin=1234,
        )
        staff_user = User.objects.create_user(username=_uname("staff"), password="x")
        self.staff = StaffProfile.objects.create(
            user=staff_user,
            hire_date=date(2020, 1, 1),
            personal_pin=4321,
            role_title="Instructor",
        )

    def _make_handoff(self, event_type="DO-AM"):
        return HandoffEvent.objects.create(
            attendance_record=self.record,
            event_type=event_type,
            pickup_person=self.pickup,
            checked_by=self.staff,
        )

    def test_child_property_resolves_through_record(self):
        handoff = self._make_handoff()
        self.assertEqual(handoff.child, self.child)

    def test_related_name_on_record(self):
        handoff = self._make_handoff()
        self.assertIn(handoff, self.record.handoff_events.all())

    def test_deleting_record_cascades_to_handoffs(self):
        handoff = self._make_handoff()
        self.record.delete()
        self.assertFalse(HandoffEvent.objects.filter(pk=handoff.pk).exists())

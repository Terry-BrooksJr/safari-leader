from datetime import date
from unittest.mock import Mock

from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase

from applications.children.models import Child
from applications.enrollment.models import Enrollment
from applications.enrollment.templatetags.schedule_extras import weekday_pills
from applications.facilities.models import Program, Site


class EnrollmentStrTest(SimpleTestCase):
    """Verify Enrollment.__str__ uses proper f-string formatting."""

    def _make_mock(self, last_name, first_name, program_str, start, end):
        mock_enrollment = Mock()
        mock_enrollment.child.last_name = last_name
        mock_enrollment.child.first_name = first_name
        mock_enrollment.program = program_str
        mock_enrollment.start_date = start
        mock_enrollment.end_date = end
        return mock_enrollment

    def test_str_with_both_dates(self):
        mock = self._make_mock(
            "Smith", "John", "Preschool", date(2024, 1, 15), date(2024, 6, 30)
        )
        result = Enrollment.__str__(mock)
        self.assertEqual(result, "Smith, John (Preschool: 2024-01-15 - 2024-06-30)")

    def test_str_with_none_end_date(self):
        mock = self._make_mock("Doe", "Jane", "Afterschool", date(2024, 9, 1), None)
        result = Enrollment.__str__(mock)
        self.assertEqual(result, "Doe, Jane (Afterschool: 2024-09-01 - None)")

    def test_str_contains_child_name(self):
        mock = self._make_mock(
            "Brooks", "Terry", "Headstart", date(2024, 3, 1), date(2025, 3, 1)
        )
        result = Enrollment.__str__(mock)
        self.assertIn("Brooks, Terry", result)
        self.assertIn("Headstart", result)

    def test_str_does_not_subtract_dates(self):
        """Regression: previous f-string had self.start_date-self.end_date."""
        mock = self._make_mock("A", "B", "P", date(2024, 1, 1), date(2024, 12, 31))
        result = Enrollment.__str__(mock)
        self.assertIn("2024-01-01", result)
        self.assertIn("2024-12-31", result)
        self.assertIn(" - ", result)

    def test_str_separates_name_with_comma_space(self):
        mock = self._make_mock(
            "Last", "First", "Prog", date(2024, 1, 1), date(2024, 2, 1)
        )
        result = Enrollment.__str__(mock)
        self.assertTrue(result.startswith("Last, First"))


class WeekdayPillsFilterTest(SimpleTestCase):
    """The weekday_pills template filter normalizes a days_of_week dict."""

    def test_orders_monday_to_sunday_regardless_of_input_order(self):
        # JSONB does not preserve key order; the filter must still be Mon-first.
        scrambled = {
            "friday": False,
            "monday": True,
            "sunday": False,
            "tuesday": True,
            "saturday": False,
            "thursday": False,
            "wednesday": False,
        }
        abbrs = [day["abbr"] for day in weekday_pills(scrambled)]
        self.assertEqual(abbrs, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])

    def test_active_flags_follow_input(self):
        result = {
            d["abbr"]: d["active"]
            for d in weekday_pills({"monday": True, "wednesday": True, "friday": True})
        }
        self.assertEqual([k for k, v in result.items() if v], ["Mon", "Wed", "Fri"])
        self.assertFalse(result["Tue"])
        self.assertFalse(result["Sun"])

    def test_missing_keys_are_inactive(self):
        result = weekday_pills({})
        self.assertEqual(len(result), 7)
        self.assertTrue(all(not day["active"] for day in result))

    def test_non_dict_input_is_safe(self):
        for bad in (None, "nope", 123, ["monday"]):
            result = weekday_pills(bad)
            self.assertEqual(len(result), 7)
            self.assertTrue(all(not day["active"] for day in result))

    def test_full_day_names_present(self):
        names = [day["name"] for day in weekday_pills({})]
        self.assertEqual(
            names,
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
        )


def _make_child(last_name="Child", status="A"):
    return Child.objects.create(
        first_name="Test",
        last_name=last_name,
        date_of_birth=date(2022, 1, 1),
        status=status,
    )


def _make_program(name="Program A", site_name="Site A"):
    site = Site.objects.create(
        name=site_name,
        address1="100 Main St, Baltimore, MD 21201",
        is_active=True,
    )
    return Program.objects.create(
        site=site,
        name=name,
        program_type="PS",
        is_active=True,
    )


class EnrollmentModelTest(TestCase):
    """Behavior added in the enrollment restructure."""

    def setUp(self):
        self.child = _make_child()
        self.program_a = _make_program("Program A", "Site A")
        self.program_b = _make_program("Program B", "Site B")

    def _enroll(self, program, status):
        return Enrollment.objects.create(
            child=self.child,
            program=program,
            start_date=date(2025, 1, 1),
            status=status,
        )

    def test_only_one_active_enrollment_per_child(self):
        self._enroll(self.program_a, "A")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._enroll(self.program_b, "A")

    def test_allows_multiple_inactive_enrollments(self):
        self._enroll(self.program_a, "A")
        # Historical/withdrawn rows for the same child are unconstrained.
        self._enroll(self.program_b, "W")
        self._enroll(self.program_a, "PS")
        self.assertEqual(self.child.enrollments.count(), 3)

    def test_different_children_can_each_be_active(self):
        other = _make_child(last_name="Other")
        self._enroll(self.program_a, "A")
        Enrollment.objects.create(
            child=other,
            program=self.program_a,
            start_date=date(2025, 1, 1),
            status="A",
        )
        self.assertEqual(Enrollment.objects.filter(status="A").count(), 2)

    def test_site_property_resolves_through_program(self):
        enrollment = self._enroll(self.program_a, "A")
        self.assertEqual(enrollment.site, self.program_a.site)

    def test_programs_m2m_and_related_names(self):
        enrollment = self._enroll(self.program_a, "A")
        # Child.programs M2M (through Enrollment) and Program.children reverse.
        self.assertIn(self.program_a, self.child.programs.all())
        self.assertIn(self.child, self.program_a.children.all())
        # related_name="enrollments" on both FKs.
        self.assertIn(enrollment, self.child.enrollments.all())
        self.assertIn(enrollment, self.program_a.enrollments.all())

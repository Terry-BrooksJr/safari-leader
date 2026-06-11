from datetime import date
from unittest.mock import Mock

from django.test import SimpleTestCase

from applications.enrollment.models import Enrollment


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
        mock = self._make_mock("Smith", "John", "Preschool", date(2024, 1, 15), date(2024, 6, 30))
        result = Enrollment.__str__(mock)
        self.assertEqual(result, "Smith, John (Preschool: 2024-01-15 - 2024-06-30)")

    def test_str_with_none_end_date(self):
        mock = self._make_mock("Doe", "Jane", "Afterschool", date(2024, 9, 1), None)
        result = Enrollment.__str__(mock)
        self.assertEqual(result, "Doe, Jane (Afterschool: 2024-09-01 - None)")

    def test_str_contains_child_name(self):
        mock = self._make_mock("Brooks", "Terry", "Headstart", date(2024, 3, 1), date(2025, 3, 1))
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
        mock = self._make_mock("Last", "First", "Prog", date(2024, 1, 1), date(2024, 2, 1))
        result = Enrollment.__str__(mock)
        self.assertTrue(result.startswith("Last, First"))

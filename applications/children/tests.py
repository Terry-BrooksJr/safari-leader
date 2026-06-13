from unittest.mock import Mock

from django.test import SimpleTestCase

from applications.children.models import AuthorizedPickupProfile, Child, MedicalNote
from applications.children.views import ChildrenList


class AuthorizedPickupProfileStrTest(SimpleTestCase):
    """Verify __str__ uses user.last_name (not last_login)."""

    def test_str_returns_last_name_comma_first_name(self):
        mock_profile = Mock()
        mock_profile.user.last_name = "Doe"
        mock_profile.user.first_name = "Jane"
        mock_profile.get_relationship_display.return_value = "Parent"
        result = AuthorizedPickupProfile.__str__(mock_profile)
        self.assertEqual(result, "Doe, Jane (Parent)")

    def test_str_does_not_include_datetime(self):
        """Regression: previously used last_login which is a datetime."""
        mock_profile = Mock()
        mock_profile.user.last_name = "Smith"
        mock_profile.user.first_name = "Bob"
        mock_profile.get_relationship_display.return_value = "Guardian"
        result = AuthorizedPickupProfile.__str__(mock_profile)
        self.assertNotIn("None", result)
        self.assertNotIn("datetime", result)


class MedicalNoteDateCreatedFieldTest(SimpleTestCase):
    """Verify date_created uses auto_now_add, not a static default."""

    def test_field_has_auto_now_add(self):
        field = MedicalNote._meta.get_field("date_created")
        self.assertTrue(field.auto_now_add)

    def test_field_is_not_editable(self):
        field = MedicalNote._meta.get_field("date_created")
        self.assertFalse(field.editable)


class ChildStrTest(SimpleTestCase):
    """Verify Child.__str__ format."""

    def test_str_format(self):
        mock_child = Mock()
        mock_child.first_name = "Billy"
        mock_child.last_name = "Kid"
        mock_child.age = 5
        result = Child.__str__(mock_child)
        self.assertEqual(result, "Child: Kid, Billy | (5)")


class ChildrenListViewConfigTest(SimpleTestCase):
    """Verify ChildrenList view is properly configured after PR changes."""

    def test_queryset_ordered_by_last_name(self):
        import inspect

        source = inspect.getsource(ChildrenList.get_queryset)
        self.assertIn('order_by("last_name")', source)

    def test_context_object_name_is_children(self):
        self.assertEqual(ChildrenList.context_object_name, "children")

    def test_extra_context_does_not_contain_children(self):
        extra = getattr(ChildrenList, "extra_context", None) or {}
        self.assertNotIn("children", extra)

    def test_paginate_by_is_25(self):
        self.assertEqual(ChildrenList.paginate_by, 25)

    def test_template_name(self):
        self.assertEqual(ChildrenList.template_name, "children/children_list.html")

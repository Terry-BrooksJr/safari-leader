from datetime import date
from unittest.mock import Mock

from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase

from applications.accounts.models import ROLES, Role, RoleAssignment, User
from applications.children.models import STUDENT_STATUS, Child

_seq = 0


def _uname(prefix):
    global _seq
    _seq += 1
    return f"{prefix}_{_seq}"


# ─── ROLES Enum Tests ───────────────────────────────────────────────────────────


class RolesChoicesTest(SimpleTestCase):
    """Verify the ROLES TextChoices enum exposes the expected members."""

    def test_contains_seven_roles(self):
        self.assertEqual(len(ROLES.choices), 7)

    def test_values(self):
        self.assertEqual(
            set(ROLES.values),
            {
                "ADMIN",
                "DIRECTOR",
                "INSTRUCTOR",
                "AIDE",
                "GUARDIAN",
                "PICKUP",
                "CLERICAL",
            },
        )

    def test_value_matches_member_name(self):
        for role in ROLES:
            self.assertEqual(role.value, role.name)

    def test_labels(self):
        self.assertEqual(str(ROLES.ADMIN.label), "Administrator")
        self.assertEqual(str(ROLES.DIRECTOR.label), "Site Director")
        self.assertEqual(str(ROLES.INSTRUCTOR.label), "Instructor")
        self.assertEqual(str(ROLES.AIDE.label), "Teacher's Aide")
        self.assertEqual(str(ROLES.GUARDIAN.label), "Guardian")
        self.assertEqual(str(ROLES.PICKUP.label), "Authorized Pickup")
        self.assertEqual(str(ROLES.CLERICAL.label), "Clerical/Auditing/Admin Support")


# ─── User Model Tests ───────────────────────────────────────────────────────────


class UserModelTest(SimpleTestCase):
    """Verify the custom User model extends Django's AbstractUser."""

    def test_subclasses_abstract_user(self):
        self.assertTrue(issubclass(User, AbstractUser))


class UserPersistenceTest(TestCase):
    """Verify the custom User model behaves like a standard auth user."""

    def test_create_user_sets_password(self):
        user = User.objects.create_user(username=_uname("user"), password="pw")
        self.assertTrue(user.check_password("pw"))
        self.assertFalse(user.check_password("wrong"))

    def test_username_is_unique(self):
        name = _uname("dupe")
        User.objects.create_user(username=name, password="pw")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(username=name, password="pw")


# ─── Role Model Tests ───────────────────────────────────────────────────────────


class RoleStrTest(SimpleTestCase):
    """Verify Role.__str__ returns the role name."""

    def test_str_returns_name(self):
        mock_role = Mock()
        mock_role.name = "ADMIN"
        self.assertEqual(Role.__str__(mock_role), "ADMIN")


class RolePersistenceTest(TestCase):
    """Verify Role persistence, defaults, and the unique-name constraint."""

    def test_create_and_str(self):
        role = Role.objects.create(name=ROLES.ADMIN, description="admins")
        self.assertEqual(str(role), "ADMIN")

    def test_name_is_unique(self):
        Role.objects.create(name=ROLES.ADMIN, description="first")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Role.objects.create(name=ROLES.ADMIN, description="second")

    def test_created_auto_populated(self):
        role = Role.objects.create(name=ROLES.DIRECTOR, description="x")
        self.assertIsInstance(role.created, date)

    def test_deleted_defaults_to_none(self):
        role = Role.objects.create(name=ROLES.AIDE, description="x")
        self.assertIsNone(role.deleted)

    def test_all_role_choices_are_persistable(self):
        for value in ROLES.values:
            Role.objects.create(name=value, description=f"{value} role")
        self.assertEqual(Role.objects.count(), len(ROLES.values))


# ─── RoleAssignment Model Tests ─────────────────────────────────────────────────


class RoleAssignmentStrTest(SimpleTestCase):
    """Verify RoleAssignment.__str__ formats as 'last, first (role)'."""

    def test_str_format(self):
        mock_ra = Mock()
        mock_ra.user.last_name = "Doe"
        mock_ra.user.first_name = "Jane"
        mock_ra.role.name = "ADMIN"
        self.assertEqual(RoleAssignment.__str__(mock_ra), "Doe, Jane (ADMIN)")


class RoleAssignmentToggleActiveTest(SimpleTestCase):
    """Verify the inherited ModelModifer.toggle_active_status flips and saves."""

    def test_toggle_from_active_to_inactive(self):
        mock_ra = Mock()
        mock_ra.is_active = True
        RoleAssignment.toggle_active_status(mock_ra)
        self.assertFalse(mock_ra.is_active)
        mock_ra.save.assert_called_once_with()

    def test_toggle_from_inactive_to_active(self):
        mock_ra = Mock()
        mock_ra.is_active = False
        RoleAssignment.toggle_active_status(mock_ra)
        self.assertTrue(mock_ra.is_active)
        mock_ra.save.assert_called_once_with()


class RoleAssignmentPersistenceTest(TestCase):
    """Verify RoleAssignment defaults, relations, and delete behaviors on the DB."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=_uname("staff"),
            password="pw",
            first_name="Jane",
            last_name="Doe",
        )
        self.role = Role.objects.create(name=ROLES.INSTRUCTOR, description="teaches")

    def _make_assignment(self, **kwargs):
        return RoleAssignment.objects.create(user=self.user, role=self.role, **kwargs)

    def test_defaults_is_active_true(self):
        ra = self._make_assignment()
        self.assertTrue(ra.is_active)

    def test_child_and_room_are_optional(self):
        ra = self._make_assignment()
        self.assertIsNone(ra.child)
        self.assertIsNone(ra.room)

    def test_created_auto_populated(self):
        ra = self._make_assignment()
        self.assertIsInstance(ra.created, date)

    def test_str_uses_user_and_role(self):
        ra = self._make_assignment()
        self.assertEqual(str(ra), "Doe, Jane (INSTRUCTOR)")

    def test_related_name_assignment(self):
        ra = self._make_assignment()
        self.assertIn(ra, self.user.assignment.all())

    def test_toggle_active_status_persists(self):
        ra = self._make_assignment()
        ra.toggle_active_status()
        ra.refresh_from_db()
        self.assertFalse(ra.is_active)
        ra.toggle_active_status()
        ra.refresh_from_db()
        self.assertTrue(ra.is_active)

    def test_user_delete_cascades(self):
        ra = self._make_assignment()
        self.user.delete()
        self.assertFalse(RoleAssignment.objects.filter(pk=ra.pk).exists())

    def test_role_delete_cascades(self):
        ra = self._make_assignment()
        self.role.delete()
        self.assertFalse(RoleAssignment.objects.filter(pk=ra.pk).exists())

    def test_child_delete_sets_null_and_keeps_assignment(self):
        child = Child.objects.create(
            first_name="Kid",
            last_name="Doe",
            date_of_birth=date(2020, 1, 1),
            status=STUDENT_STATUS.ENROLLED,
        )
        ra = self._make_assignment(child=child)
        child.delete()
        ra.refresh_from_db()
        self.assertIsNone(ra.child_id)
        self.assertTrue(RoleAssignment.objects.filter(pk=ra.pk).exists())

"""Unit tests for :mod:`common.backends.storage_backends`.

The three storage classes subclass django-storages' ``S3Boto3Storage``. These
tests assert the declared class attributes and exercise ``StaticStorage``'s
required-settings validation. The real S3 backend ``__init__`` is patched out so
no boto3 client is ever constructed, and ``override_settings`` is used to drive
the validation branches.
"""

from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings
from storages.backends.s3boto3 import S3Boto3Storage

from common.backends.storage_backends import (
    PrivateMediaStorage,
    PublicMediaStorage,
    StaticStorage,
)

# A complete set of the S3 settings StaticStorage.__init__ requires.
_VALID_S3_SETTINGS = {
    "AWS_ACCESS_KEY_ID": "key",
    "AWS_S3_ENDPOINT_URL": "https://s3.example.com",
    "AWS_SECRET_ACCESS_KEY": "secret",
    "AWS_STORAGE_BUCKET_NAME": "bucket",
    "AWS_S3_REGION_NAME": "us-east-1",
}


# ─── StaticStorage attributes ───────────────────────────────────────────────


class StaticStorageAttributesTest(SimpleTestCase):
    """Verify StaticStorage's declared class attributes."""

    def test_is_s3_backend(self):
        self.assertTrue(issubclass(StaticStorage, S3Boto3Storage))

    def test_location(self):
        self.assertEqual(StaticStorage.location, "static")

    def test_default_acl_is_public_read(self):
        self.assertEqual(StaticStorage.default_acl, "public-read")


# ─── StaticStorage.__init__ validation ──────────────────────────────────────


class StaticStorageInitValidationTest(SimpleTestCase):
    """Verify the required-settings guard in StaticStorage.__init__.

    ``S3Boto3Storage.__init__`` is patched to a no-op so instantiation never
    builds a real boto3 client; only the validation logic is under test.
    """

    @override_settings(**_VALID_S3_SETTINGS)
    def test_init_succeeds_when_all_settings_present(self):
        with patch.object(S3Boto3Storage, "__init__", return_value=None) as mock_init:
            storage = StaticStorage()
        self.assertIsInstance(storage, StaticStorage)
        mock_init.assert_called_once()

    @override_settings(**{**_VALID_S3_SETTINGS, "AWS_ACCESS_KEY_ID": ""})
    def test_init_raises_when_required_setting_is_empty(self):
        with patch.object(S3Boto3Storage, "__init__", return_value=None):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                StaticStorage()
        self.assertIn("AWS_ACCESS_KEY_ID", str(ctx.exception))

    @override_settings(**_VALID_S3_SETTINGS)
    def test_init_raises_when_required_setting_is_absent(self):
        with patch.object(S3Boto3Storage, "__init__", return_value=None):
            # Deleting on the override holder makes hasattr() return False,
            # exercising the `not hasattr(...)` half of the guard.
            del settings.AWS_S3_ENDPOINT_URL
            with self.assertRaises(ImproperlyConfigured) as ctx:
                StaticStorage()
        self.assertIn("AWS_S3_ENDPOINT_URL", str(ctx.exception))

    @override_settings(
        **{**_VALID_S3_SETTINGS, "AWS_ACCESS_KEY_ID": "", "AWS_SECRET_ACCESS_KEY": ""}
    )
    def test_init_reports_every_missing_setting(self):
        with patch.object(S3Boto3Storage, "__init__", return_value=None):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                StaticStorage()
        message = str(ctx.exception)
        self.assertIn("AWS_ACCESS_KEY_ID", message)
        self.assertIn("AWS_SECRET_ACCESS_KEY", message)

    @override_settings(**_VALID_S3_SETTINGS)
    def test_init_delegates_to_super_when_valid(self):
        with patch.object(S3Boto3Storage, "__init__", return_value=None) as mock_init:
            StaticStorage()
        # Validation passed, so the base S3 backend init is invoked with no
        # positional/keyword args of its own.
        mock_init.assert_called_once_with()


# ─── PublicMediaStorage attributes ──────────────────────────────────────────


class PublicMediaStorageAttributesTest(SimpleTestCase):
    """Verify PublicMediaStorage's declared class attributes."""

    def test_is_s3_backend(self):
        self.assertTrue(issubclass(PublicMediaStorage, S3Boto3Storage))

    def test_location(self):
        self.assertEqual(PublicMediaStorage.location, "/public")

    def test_default_acl_is_public_read(self):
        self.assertEqual(PublicMediaStorage.default_acl, "public-read")

    def test_does_not_overwrite_files(self):
        self.assertFalse(PublicMediaStorage.file_overwrite)

    def test_base_url_built_from_custom_domain(self):
        # base_url is computed at import time as f"{domain}/{location}/"; with a
        # leading-slash location this yields a double slash before "public".
        self.assertEqual(
            PublicMediaStorage.base_url,
            f"{settings.AWS_S3_CUSTOM_DOMAIN}//public/",
        )


# ─── PrivateMediaStorage attributes ─────────────────────────────────────────


class PrivateMediaStorageAttributesTest(SimpleTestCase):
    """Verify PrivateMediaStorage's declared class attributes."""

    def test_is_s3_backend(self):
        self.assertTrue(issubclass(PrivateMediaStorage, S3Boto3Storage))

    def test_location(self):
        self.assertEqual(PrivateMediaStorage.location, "restricted")

    def test_default_acl_is_private(self):
        self.assertEqual(PrivateMediaStorage.default_acl, "private")

    def test_overwrites_files(self):
        self.assertTrue(PrivateMediaStorage.file_overwrite)

    def test_uses_custom_domain(self):
        self.assertTrue(PrivateMediaStorage.custom_domain)

    def test_base_url_built_from_custom_domain(self):
        self.assertEqual(
            PrivateMediaStorage.base_url,
            f"{settings.AWS_S3_CUSTOM_DOMAIN}/restricted/",
        )

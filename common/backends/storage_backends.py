"""
Module: common.backends.storage_backends

This module contains custom classes for S3Boto3Storage, which are used for storing static, public media, and private media files in AWS S3.

Classes:
- StaticStorage: Used for storing static files in AWS S3.
- PublicMediaStorage: Used for storing public media files in AWS S3.
- PrivateMediaStorage: Used for storing private media files in AWS S3.

Attributes:
- location: The location in AWS S3 where the files will be stored.
- file_overwrite: Specifies whether existing files should be overwritten.
- bucket_name: The name of the bucket where the files will be stored.
- default_acl: The default access control list for the files.
- custom_domain: Specifies whether a custom domain is used for accessing the files.

Usage:
To use these custom classes, simply import them and specify the appropriate settings in your Django settings file.

Example:
```python
# settings.py
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = settings.AWS_STATIC_LOCATION

class PublicMediaStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False

class PrivateMediaStorage(S3Boto3Storage):
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    bucket_name = settings.AWS_PRIVATE_BUCKET_NAME
    default_acl = 'private'
    file_overwrite = False
custom_domain = False

"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Provides storage for static files in AWS S3 with public-read access.
    Ensures all required S3 settings are present before initializing the storage backend.
    """

    location = "static"
    default_acl = "public-read"

    def __init__(self, *args, **kwargs):
        required_settings = ["AWS_ACCESS_KEY_ID", "AWS_S3_ENDPOINT_URL", "AWS_SECRET_ACCESS_KEY", "AWS_STORAGE_BUCKET_NAME", "AWS_S3_REGION_NAME", " "]

        if missing_settings := [setting for setting in required_settings if not hasattr(settings, setting) or not getattr(settings, setting)]:
            raise ImproperlyConfigured(f"The following required S3 settings are missing or empty: " f"{', '.join(missing_settings)}")

        super().__init__(*args, **kwargs)


class PublicMediaStorage(S3Boto3Storage):
    """
    Provides storage for public media files in AWS S3 with public-read access.
    Ensures media files are not overwritten and are accessible via a custom domain.
    """

    location = "/public"
    default_acl = "public-read"
    file_overwrite = False
    base_url = f"{settings.AWS_S3_CUSTOM_DOMAIN}/{location}/"


class PrivateMediaStorage(S3Boto3Storage):
    """
    Provides storage for private media files in AWS S3 with restricted access.
    Ensures files are stored privately and are accessible only through authenticated requests.
    """

    location = "restricted"
    default_acl = "private"
    file_overwrite = True
    custom_domain = True
    base_url = f"{settings.AWS_S3_CUSTOM_DOMAIN}/{location}/"
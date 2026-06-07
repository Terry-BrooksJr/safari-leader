"""
Root conftest for pytest-django.

In CI, Doppler injects all required env vars (SECRET_KEY, FERNET_KEYS, AWS_*, etc.)
before pytest runs. Locally, run tests via:
    doppler run -- task run:test
or export the required env vars manually.

The defaults below cover the case where pytest imports this conftest early enough
to set them before Django settings are loaded.
"""
import os

_TEST_DEFAULTS = {
    "SECRET_KEY": "test-secret-key-not-for-production",
    "FERNET_KEYS": "dGVzdGtleS1mb3ItdGVzdGluZy1vbmx5LTEyMzQ1Njc4OQ==",
    "RECAPTCHA_PUBLIC_KEY": "test",
    "RECAPTCHA_PRIVATE_KEY": "test",
    "AWS_ACCESS_KEY_ID": "test",
    "AWS_SECRET_ACCESS_KEY": "test",
    "AWS_DEFAULT_REGION": "us-east-1",
    "AWS_STORAGE_BUCKET_NAME": "test-bucket",
    "AWS_S3_CUSTOM_DOMAIN": "test.example.com",
    "POSTGRES_DB": "safari_leader_test",
    "PG_DATABASE_USER": "postgres",
    "PG_DATABASE_PASSWORD": "",
    "PG_DATABASE_HOST": "localhost",
    "PG_DATABASE_PORT": "5432",
}

for _key, _value in _TEST_DEFAULTS.items():
    os.environ.setdefault(_key, _value)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

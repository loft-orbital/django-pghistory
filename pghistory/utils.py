import django
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.version import get_version_tuple

# Django>=3.1 changes the location of JSONField
if django.VERSION >= (3, 1):
    from django.db.models import JSONField as DjangoJSONField
else:  # pragma: no cover
    from django.contrib.postgres.fields import JSONField as DjangoJSONField


def _psycopg_version():
    try:
        import psycopg as Database
    except ImportError:
        import psycopg2 as Database
    except Exception as exc:  # pragma: no cover
        raise ImproperlyConfigured("Error loading psycopg2 or psycopg module") from exc

    version_tuple = get_version_tuple(Database.__version__.split(" ", 1)[0])

    if version_tuple[0] not in (2, 3):  # pragma: no cover
        raise ImproperlyConfigured(f"Pysocpg version {version_tuple[0]} not supported")

    return version_tuple


psycopg_version = _psycopg_version()
psycopg_maj_version = psycopg_version[0]


class JSONField(DjangoJSONField):
    """
    Creates a consistent import path for JSONField regardless of Django
    version.
    """


def related_model(field):
    """Return the concrete model a field references"""
    if hasattr(field, "related_model") and field.related_model:
        return field.related_model._meta.concrete_model


def _can_proxy_user_model() -> bool:
    """
    Return whether the User model is set up and the corresponding app is installed.
    """
    auth_user_model = getattr(settings, "AUTH_USER_MODEL", None)
    if not auth_user_model:
        return False
    try:
        app_label, _model_name = auth_user_model.split(".", 1)
    except ValueError:
        return False
    return apps.is_installed(app_label)

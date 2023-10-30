"""
Django creates redundant migrations
for Django model changes that do not alter the database.

Here we patch djangos migration machinery to ignore attrs.

The management commands `makemigrations` and `migrate`
will ignore the attrs defined in:

    - MIGRATION_IGNORE_MODEL_ATTRS
    - MIGRATION_IGNORE_FIELD_ATTRS
    - MIGRATION_IGNORE_FILE_FIELD_ATTRS
    - MIGRATION_IGNORE_RELATED_FIELD_ATTRS

This will reduce the amount of migrations and therefore speed-up development
"""

import logging
from functools import wraps

from django.db.migrations.operations import AlterModelOptions
from django.db.models import Field, FileField
from django.db.models.fields.related import RelatedField
from wagtail.fields import StreamField

logger = logging.getLogger(__name__)

MIGRATION_IGNORE_MODEL_ATTRS = ["verbose_name", "verbose_name_plural"]
MIGRATION_IGNORE_FIELD_ATTRS = ["validators", "choices", "help_text", "verbose_name"]
MIGRATION_IGNORE_FILE_FIELD_ATTRS = ["upload_to", "storage"]

MIGRATION_IGNORE_RELATED_FIELD_ATTRS = ["related_query_name"]

for attr in MIGRATION_IGNORE_MODEL_ATTRS:
    logger.info(f"Model {attr} attr will be ignored.")

for attr in MIGRATION_IGNORE_FIELD_ATTRS:
    logger.info(f"Field {attr} attr will be ignored.")

for attr in MIGRATION_IGNORE_FILE_FIELD_ATTRS:
    logger.info(f"File field {attr} attr will be ignored.")

for attr in MIGRATION_IGNORE_RELATED_FIELD_ATTRS:
    logger.info(f"Related field {attr} attr will be ignored.")

logger.info("Stream field attrs will be ignored.")


def patch_ignored_model_attrs(cls):
    for attr in MIGRATION_IGNORE_MODEL_ATTRS:
        if attr in cls.ALTER_OPTION_KEYS:
            cls.ALTER_OPTION_KEYS.remove(attr)


def patch_field_deconstruct(old_func):
    @wraps(old_func)
    def deconstruct_with_ignored_attrs(self):
        name, path, args, kwargs = old_func(self)
        for attr in MIGRATION_IGNORE_FIELD_ATTRS:
            kwargs.pop(attr, None)
        return name, path, args, kwargs

    return deconstruct_with_ignored_attrs


def patch_file_field_deconstruct(old_func):
    @wraps(old_func)
    def deconstruct_with_ignored_attrs(self):
        name, path, args, kwargs = old_func(self)
        for attr in MIGRATION_IGNORE_FILE_FIELD_ATTRS:
            kwargs.pop(attr, None)
        return name, path, args, kwargs

    return deconstruct_with_ignored_attrs


def patch_related_field_deconstruct(old_func):
    @wraps(old_func)
    def deconstruct_with_ignored_attrs(self):
        name, path, args, kwargs = old_func(self)
        for attr in MIGRATION_IGNORE_RELATED_FIELD_ATTRS:
            kwargs.pop(attr, None)
        return name, path, args, kwargs

    return deconstruct_with_ignored_attrs


def patch_stream_field_deconstruct(old_func):
    @wraps(old_func)
    def deconstruct_without_block_types(self):
        name, path, args, kwargs = old_func(self)
        args = [[]]
        return name, path, args, kwargs

    return deconstruct_without_block_types


Field.deconstruct = patch_field_deconstruct(Field.deconstruct)
FileField.deconstruct = patch_file_field_deconstruct(FileField.deconstruct)
RelatedField.deconstruct = patch_related_field_deconstruct(RelatedField.deconstruct)
StreamField.deconstruct = patch_stream_field_deconstruct(StreamField.deconstruct)
patch_ignored_model_attrs(AlterModelOptions)

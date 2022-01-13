import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from chatApplication.errors.api_errors import APIError


class UserManager(models.Manager):
    def get_or_create(self, **kwargs):
        regex = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+_-]{1,16}[A-Za-z0-9]$")
        username_field = 'username'
        if username_field in kwargs:
            if len(kwargs[username_field]) > settings.USERNAME_MAX_LENGTH:
                raise ValidationError(message="Username must be at-least 3 chars")
            if not regex.match(kwargs[username_field]):
                raise ValidationError(["Username must have alphanumeric start and end char.",
                                       "Only - . _ special characters are allowed"])

        return super().get_or_create(**kwargs)

    def api_get_or_create(self, **kwargs):
        try:
            return self.get_or_create(**kwargs)
        except ValidationError as e:
            raise APIError(e.messages)


class User(models.Model):
    objects = UserManager()

    username = models.CharField(max_length=settings.USERNAME_MAX_LENGTH, unique=True, null=False, db_index=True)

    def __repr__(self):
        return f'(User: {self.username})'

    def __str__(self):
        return f'(User: {self.username})'

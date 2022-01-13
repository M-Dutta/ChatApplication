from django.conf import settings
from django.db import models

from chatApplication.errors.api_errors import APIError


class UserManager(models.Manager):
    def api_get(self, **kwargs):
        try:
            return super().get(**kwargs)
        except User.DoesNotExist:
            raise APIError(f"User with values {kwargs} does not exist")


class User(models.Model):
    objects = UserManager()

    username = models.CharField(max_length=settings.USERNAME_MAX_LENGTH, unique=True, null=False, db_index=True)



    def __repr__(self):
        return f'(User: {self.username})'

    def __str__(self):
        return f'(User: {self.username})'

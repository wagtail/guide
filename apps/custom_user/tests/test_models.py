from unittest import TestCase

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from apps.custom_user.models import User


class TestCustomUser(TestCase):
    def test_custom_user(self):
        self.assertIsInstance(User(), AbstractUser)
        self.assertIsInstance(get_user_model()(), User)

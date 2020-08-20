from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    stripe_customer_id = models.CharField(max_length=100)

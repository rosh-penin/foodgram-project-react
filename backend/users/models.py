from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField("Email address")
    first_name = models.CharField('First Name', max_length=20)
    last_name = models.CharField('Last Name', max_length=30)
    is_subscribed = models.BooleanField('Subscribed?', default=False)


from django.contrib.auth.models import AbstractUser
from django.db import models


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    # project = models.CharField(max_length=100, default='wtc')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
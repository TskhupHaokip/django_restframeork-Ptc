from django.contrib.auth.models import User
from django.db import models

class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="books")
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)

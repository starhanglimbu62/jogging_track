from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    roles = (
        ('USER', 'Regular User'), 
        ('MANAGER', 'User Manager'), 
        ('ADMIN', 'Administrator')
    )
    role = models.CharField(choices=roles, default=roles[0][0], max_length=20)

class Entry(models.Model):
    user = models.ForeignKey(User, related_name='entry', null=True, on_delete=models.CASCADE)
    distance = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=1)
    date = models.DateField(default=timezone.now)
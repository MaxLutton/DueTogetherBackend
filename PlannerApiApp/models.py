from django.db import models
from django.contrib.auth import get_user_model
import datetime

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    owner = models.ForeignKey('auth.User', related_name='owned_tasks', on_delete=models.CASCADE)
    assignee = models.ForeignKey('auth.User', related_name='assigned_tasks', on_delete=models.CASCADE, null=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    dueDate = models.DateTimeField(default=datetime.datetime.now() + datetime.timedelta(days=7))
    points = models.IntegerField(default=0)
    completedDate = models.DateTimeField(blank=True, null=True)
    foo = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.title



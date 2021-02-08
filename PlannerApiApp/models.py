from django.db import models
from django.contrib.auth import get_user_model
import datetime


def todayPlusWeek():
    return datetime.datetime.now() + datetime.timedelta(days=7)

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    owner = models.ForeignKey('auth.User', related_name='owned_tasks', on_delete=models.CASCADE)
    assignee = models.ForeignKey('auth.User', related_name='assigned_tasks', on_delete=models.CASCADE, null=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    dueDate = models.DateTimeField(default=todayPlusWeek)
    points = models.IntegerField(default=0)
    completedDate = models.DateTimeField(blank=True, null=True)
    team = models.ForeignKey('Team', related_name='team_tasks', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

class Team(models.Model):
    name = models.CharField(max_length=50)
    team_owner = models.ForeignKey('auth.User', related_name='team_owner', on_delete=models.CASCADE)
    team_members = models.ManyToManyField(get_user_model(), related_name="teams")
    team_total_points = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    user_total_points = models.IntegerField(default=0)

class Point(models.Model):
    value = models.IntegerField(default=1, null=False)
    current_total_user = models.IntegerField(default=0, null=False)
    current_total_team = models.IntegerField(default=0, null=True)
    date = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(Team, models.CASCADE, related_name='team_points', null=True)
    user = models.ForeignKey(UserProfile, models.CASCADE, related_name='user_points', null=True)

class TeamRequest(models.Model):
    from_user = models.ForeignKey("auth.User", related_name="from_user", on_delete=models.CASCADE)
    to_team = models.ForeignKey(Team, related_name="to_team", on_delete=models.CASCADE)


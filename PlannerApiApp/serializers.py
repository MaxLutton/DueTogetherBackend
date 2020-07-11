from rest_framework import serializers
from .models import Task, Team
from django.contrib.auth.models import User

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    assignee = serializers.ReadOnlyField(source='assignee.username')
    team = serializers.SlugRelatedField(queryset=Team.objects.all(), slug_field="name", required=False)
    class Meta:
        model = Task
        # To serialize all fields
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    team_owner = serializers.StringRelatedField()
    team_members = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", many=True, required=False)
    team_tasks = TaskSerializer(many=True, required=False)
    class Meta:
        model = Team
        fields = ('name', 'team_owner', 'team_members', 'team_tasks')
    

class UserSerializer(serializers.ModelSerializer):
    owned_tasks = TaskSerializer(many=True, required=False)
    assigned_tasks = TaskSerializer(many=True, required=False)
    password = serializers.CharField(write_only=True)
    teams = TeamSerializer(many=True, required=False)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    
    class Meta:
        model = User
        # To serialize all fields
        fields = ('id', 'username', 'password', 'owned_tasks', 'assigned_tasks', 'teams')


from rest_framework import serializers
from .models import Task, Team
from django.contrib.auth.models import User

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    assignee = serializers.ReadOnlyField(source='assignee.username')
    class Meta:
        model = Task
        # To serialize all fields
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    #team_owner = serializers.ReadOnlyField(source='team_owner.username')
    team_owner = serializers.StringRelatedField()
    #team_members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    team_members = serializers.StringRelatedField(many=True, required=False)
    class Meta:
        model = Team
        fields = '__all__'
    

class UserSerializer(serializers.ModelSerializer):
    #owned_tasks = serializers.PrimaryKeyRelatedField(many=True, queryset=Task.objects.all(), required=False)
    owned_tasks = TaskSerializer(many=True, required=False)
    #assigned_tasks = serializers.PrimaryKeyRelatedField(many=True, queryset=Task.objects.all(), required=False)
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


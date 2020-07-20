from rest_framework import serializers
import logging
from .models import Task, Team, UserProfile
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        # To serialize all fields
        fields = '__all__'
    owner = serializers.ReadOnlyField(source='owner.username')
    assignee = serializers.ReadOnlyField(source='assignee.username')
    team = serializers.SlugRelatedField(queryset=Team.objects.all(), slug_field="name", required=False)


class TeamSerializer(serializers.ModelSerializer):
    team_owner = serializers.StringRelatedField()
    team_members = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", many=True, required=False)
    team_tasks = TaskSerializer(many=True, required=False)
    class Meta:
        model = Team
        fields = ('name', 'team_owner', 'team_members', 'team_tasks', 'id')
    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        #fields = ('user_points')
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # To serialize all fields
        fields = ('id', 'username', 'password', 'owned_tasks', 'assigned_tasks', 'teams', 'profile')
        #fields = '__all__'
        extra_kwrgs = {'password': {'write_only': True}} # Use password for deserialization only.
    
    # Writable Nested Serializers
    owned_tasks = TaskSerializer(many=True, required=False)
    assigned_tasks = TaskSerializer(many=True, required=False)
    password = serializers.CharField(write_only=True)
    teams = TeamSerializer(many=True, required=False)
    profile = UserProfileSerializer(required=False) 

    def create(self, validated_data):
        profile_data = validated_data.get("profile")
        # Set defaults. Probably want to fix this later...
        if not profile_data:
            profile_data = {"user_points": 0}
        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password']) # Stores password as a hash.
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        logger.warning("Got: {}".format(validated_data))
        profile_data = validated_data.get('profile')
        profile = instance.profile

        # Allow user to change their username.
        instance.username = validated_data.get('username', instance.username)
        instance.save()

        # Allow user to update their points total.
        profile.user_points = profile_data.get("user_points", profile.user_points)
        profile.save()

        return instance

    



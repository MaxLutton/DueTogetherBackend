from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    assignee = serializers.ReadOnlyField(source='assignee.username')
    class Meta:
        model = Task
        # To serialize all fields
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    owned_tasks = serializers.PrimaryKeyRelatedField(many=True, queryset=Task.objects.all(), required=False)
    assigned_tasks = serializers.PrimaryKeyRelatedField(many=True, queryset=Task.objects.all(), required=False)
    password = serializers.CharField(write_only=True)

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
        fields = ('id', 'username', 'password', 'owned_tasks', 'assigned_tasks')
    
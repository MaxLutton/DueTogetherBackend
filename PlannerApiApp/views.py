from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # If used custom user model
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

import logging

from .serializers import TaskSerializer, UserSerializer
from .models import Task
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)

# Create your views here.
# Use for GET many and POST new Tasks.
class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Allow filtering on specified fields.
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'title': ['exact'],
        'completed': ['exact'],
        'owner': ['exact'],
        'assignee': ['exact'],
        'createdDate': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'dueDate': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'points': ['gte', 'lte', 'exact', 'gt', 'lt']
    }

    def perform_create(self, serializer):
        # Automatically make the task's creator the owner.
        serializer.save(owner=self.request.user)
        # Save assignee by looking up username.
        assigneeUsername = self.request.data.get("assignee")
        if assigneeUsername and User.objects.filter(username=assigneeUsername).exists():
            assigneeObject = User.objects.get(username=assigneeUsername)
            serializer.save(assignee=assigneeObject)

# Use for GET, PUT, Delete Tasks.
class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # Override for updating the assignee
    def perform_update(self, serializer):
        assigneeUsername = self.request.data.get("assignee")
        if assigneeUsername and User.objects.filter(username=assigneeUsername).exists():
            assigneeObject = User.objects.get(username=assigneeUsername)
            serializer.save(assignee=assigneeObject)
    
# Use for getting API help info.
@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'List': '/tasks',
        'Detail': '/tasks/<str:pk>/',
        'Users': '/users/',
        'User Detail': '/users/<str:pk>/',
        'User Create': '/users/register/'
    }
    return Response(api_urls)

# Use for GET on many Users.
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Use for GET on individual Users.
class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# From: https://stackoverflow.com/questions/16857450/how-to-register-users-in-django-rest-framework
class UserCreate(generics.CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer
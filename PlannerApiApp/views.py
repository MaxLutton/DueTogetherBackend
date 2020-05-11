from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # If used custom user model
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import TaskSerializer, UserSerializer
from .models import Task
from .permissions import IsOwnerOrReadOnly


# Create your views here.
# Use for GET many and POST new Tasks.
class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Use for GET, PUT, Delete Tasks.
class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
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
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from fcm_django.api.rest_framework import FCMDeviceViewSet
from . import views

'''
urlpatterns = [
    path('', views.apiOverview, name='api-overview'),
    path('tasks/', views.TaskList.as_view()),
    path('tasks/<int:pk>/', views.TaskDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('users/register/', views.UserCreate.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('teams/', views.TeamList.as_view()),
    path('teams/<int:pk>/', views.TeamDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
'''

from django.conf.urls import re_path, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'devices', FCMDeviceViewSet)

urlpatterns = [
    re_path(r'^', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('teams/<int:pk>/team_request/', views.TeamViewSet.as_view({"get": "get_team_requests", "post": "create_team_request"})),
    path('teams/<int:pk>/team_request/<int:request_id>/accept/', views.TeamViewSet.as_view({"post": "accept_team_request"})),
    path('teams/<int:pk>/team_request/<int:request_id>/reject/', views.TeamViewSet.as_view({"post": "reject_team_request"})),
]
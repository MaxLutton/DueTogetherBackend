from django.contrib.auth.models import User
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status
import logging

from .serializers import TaskSerializer, UserSerializer, TeamSerializer, TeamRequestSerializer
from .models import Task, Team, TeamRequest
from .permissions import IsOwnerOrReadOnly, IsTeamOwnerOrReadyOnly, IsSelfOrAdmin, IsOnTeam

logger = logging.getLogger(__name__)

# Use for GET many and POST new Tasks.
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        # TODO: Add permission class for assignee or team member!
        if self.action == "list" or self.action == "retrieve" or self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrReadOnly]
        return  [permission() for permission in permission_classes]

    # Allow filtering on specified fields.
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'title': ['exact'],
        'completed': ['exact'],
        'owner': ['exact'],
        'assignee': ['exact'],
        'createdDate': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'dueDate': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'points': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'team': ['exact']
    }

    def perform_create(self, serializer):
        # Automatically make the task's creator the owner.
        serializer.save(owner=self.request.user)
        # Save assignee by looking up username.
        assigneeUsername = self.request.data.get("assignee")
        if assigneeUsername and User.objects.filter(username=assigneeUsername).exists():
            assigneeObject = User.objects.get(username=assigneeUsername)
            serializer.save(assignee=assigneeObject)

    # Override for updating the assignee
    def perform_update(self, serializer):
        logger.warning("Data: {}".format(self.request.data))
        assigneeUsername = self.request.data.get("assignee")
        teamName = self.request.data.get("team")
        points = self.request.data.get("points")
        data = {}
        if assigneeUsername and User.objects.filter(username=assigneeUsername).exists():
            logging.warning("Updating assignee: {}".format(assigneeUsername))
            assigneeObject = User.objects.get(username=assigneeUsername)
            data["assignee"] = assigneeObject
        elif assigneeUsername and not User.objects.filter(username=assigneeUsername).exists():
            logger.error("Invalid assignee username {}".format(assigneeUsername))
            # TODO: Raise Invalid Request Error
        if teamName and Team.objects.filter(name=teamName).exists():
            logging.warning("Updating team name {}".format(teamName))
            teamObject = Team.objects.get(name=teamName)
            data["team"] = teamObject
        elif teamName and not Team.objects.filter(name=teamName).exists():
            logger.error("Invalid team name {}".format(teamName))
            # TODO: Raise Invalid Request Error
        if points is not None:
            logging.warning("Updating points value to {}".format(points))
            data["points"] = int(points)
        if self.request.data.get("completed") is not None:
            data["completed"] = self.request.data.get("completed")
        serializer.save(**data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            logger.warning("Allowing any")
            permission_classes = [permissions.AllowAny]
        elif self.action == "update" or self.action == "partial_update":
            permission_classes = [IsSelfOrAdmin]
        elif self.action == "create_team_request":
            permission_classes = [permissions.IsAuthenticated]
            logging.warning("HI")
        else:
            permission_classes = [permissions.IsAdminUser]
        return  [permission() for permission in permission_classes]
        

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def perform_create(self, serializer):
        # Automatically make team's creator the owner
        serializer.save(team_owner=self.request.user, team_members=[self.request.user])

    def perform_update(self, serializer):
        memberUsernames = self.request.data.get("team_members")
        if memberUsernames:
            membersToAdd = []
            for user in memberUsernames:
                if User.objects.filter(username=user).exists():
                    logger.warning("Adding user: {}".format(user))
                    membersToAdd.append(User.objects.get(username=user))
                else:
                    logger.error("User not found: {}".format(user))
                    # TODO: Raise Error
            serializer.save(team_members=membersToAdd)

    def get_permissions(self):
        logger.warning(f"IT IS {self.action}")
        if self.action == "list" or self.action == "retrieve" or self.action == "create" or self.action == "create_team_request":
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "get_team_requests" or self.action == "accept_team_request" or self.action == "reject_team_request":
            permission_classes = [IsOnTeam]
        else:
            permission_classes = [IsTeamOwnerOrReadyOnly]
            # TODO: Want to add admin access...
        return  [permission() for permission in permission_classes]
    
    @action(methods=["post"], detail=True)
    def create_team_request(self, request, pk=None):
        from_user = request.user
        to_team = self.get_object()
        instance, created = TeamRequest.objects.get_or_create(from_user=from_user, to_team=to_team)
        serializer = TeamRequestSerializer(instance=instance)
        if created:
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=["post"], detail=True)
    def reject_team_request(self, request, pk=None, *args, **kwargs):
        request_id = kwargs["request_id"]
        instance = TeamRequest.objects.get(id=request_id)
        instance.delete()
        return Response(status=status.HTTP_200_OK)
    
    @action(methods=["post"], detail=True)
    def accept_team_request(self, request, pk=None, *args, **kwargs):
        request_id = kwargs["request_id"]
        instance = TeamRequest.objects.get(id=request_id)
        user = instance.from_user
        team = self.get_object()
        instance.delete()
        if user:
            logger.warning(f"Adding user: {user}")
            team.team_members.add(user)
            serializer = TeamSerializer(team, data={"name": team.name})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return  Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def get_team_requests(self, request, pk=None):
        team = self.get_object()
        team_reqs = TeamRequest.objects.filter(to_team=team)
        req_data = []
        for req in team_reqs:
            req_data.append(TeamRequestSerializer(instance=req).data)
        return Response(data=req_data, status=status.HTTP_200_OK)

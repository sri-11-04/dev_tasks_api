from rest_framework import viewsets,status,filters
from .serializers import UserSerializer,ProjectCommentSerializer,TaskSerializer,TeamMembersSerializer\
    ,TeamSerializer,ProjectsSerializer,NotificationSerializer,serializers,ProjectTeamSerializer,TaskAssignmentSerializer
from .models import User,Tasks,ProjectComments,Team,TeamMembers,Projects,Notification,ProjectTeams,TaskAssignment
from rest_framework.decorators import action
from rest_framework.response import Response
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from copy import deepcopy
from typing import Any
from .permissions import CustomPermissions
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TaskAssignmentFilter,TasksFilter,TeamFilter,TeamMembersFilter,ProjectCommentsFilter\
    ,ProjectFilter,ProjectTeamFilter,UserFilter



# Create your views here.

class UserViews(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['username','id','email','bio','is_active','is_staff','is_superuser','last_login','created_at']
    search_fields = ['username','email']
   

    # details = False => no lookups (no params => pk or any filter query) , details = True => lookups (there will be a pk)
    @action(detail=False, methods=['post'],permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully!", "user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # login method instead of url path of token 
    '''
    # manual token login instead of url path
    @action(detail=False,methods=['post'])
    def login(self,request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email=serializer.validated_data['username']
            password=serializer.validated_data['password']
            user = authenticate(email=email,password=password)

            if user:
               data = {
                   'email':email,
                   'password':password
               }
               token = TokenObtainPairSerializer(data=data)
               if token.is_valid():
                   return Response(token.validated_data,status=status.HTTP_200_OK)
               else:
                   return Response(token.errors,status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error':'invalid creditionals'},status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        '''
    
    # logout method
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logout the user by blacklisting the refresh token.
        """
        # print(request.user,'as user')
        try:
            refresh_token = request.data.get("refresh")
            # print(f'{refresh_token = }')
            if not refresh_token:
                return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  #Blacklist the refresh token

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # me method   
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user  # Use authenticated user directly

        if request.method == 'GET':
            serializer = self.get_serializer(user)  # Serialize user data
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamViews(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    def get_serializer_class(self):
        if self.action == 'members':
            return TeamMembersSerializer
        return TeamSerializer
    
    def get_filterset_class(self):
        if self.action == 'members' and self.request.method == 'GET':
            return TeamMembersFilter
        return TeamFilter

    # over riding this because when an team is created it is defined with an tl also so we also create an entry for the tl in TeamMember model
    @transaction.atomic()
    def perform_create(self, serializer):
        instance =  serializer.save()   # it gives the current created object's instance
        data = {
                'team':instance.id,
                'user':instance.team_lead.id,
                'role':'Team Lead'
            }
        Team_memb_serializer = TeamMembersSerializer(data=data)
        if Team_memb_serializer.is_valid():
            Team_memb_serializer.save()
        else:
            raise serializers.ValidationError(Team_memb_serializer.errors)
        

    @transaction.atomic()
    @action(detail=True,methods=['post','get','patch','delete'],url_path='members(?:/(?P<member_id>[^/.]+))?')  #here we define the url path as we needed with help of regx to satisfy our needs
    # point to note request is what they give as json data or payload to access url args just give the url para name itself inthis case mrmber_id
    def members(self,request,pk=None,member_id=None):
        team = self.get_object()
        print(team.id)
        if request.method == 'GET':
            if member_id:
                obj = TeamMembers.objects.filter(pk=member_id).first()
                if not obj: return Response({'error':'member id not found'},status=status.HTTP_404_NOT_FOUND)
                serializer = self.get_serializer(obj)
                return Response(serializer.data,status=status.HTTP_200_OK)
            obj = TeamMembers.objects.filter(team=team.id)
            serializer = TeamMembersSerializer(obj,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        elif request.method == 'POST':
            # here we check if the user already in the team member if so why should we add him again
            user_id = request.data.get("user")  # Extract user ID from request
            if TeamMembers.objects.filter(team=team, user_id=user_id).exists():
                return Response({'error': 'User is already a member of this team'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = TeamMembersSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        elif request.method in ('PATCH','DELETE'):
            if member_id:
                print(f'{request.data.get('member_id') = }')
                print(f'{member_id = }')
                try:
                    member = TeamMembers.objects.get(pk=member_id,team=team)  # Ensure user is in the same team
                except TeamMembers.DoesNotExist:
                    return Response({'detail':'member_id not found'},status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'detail':str(e)},status=status.HTTP_400_BAD_REQUEST)

                if request.method == 'PATCH':
                        member_serializer = TeamMembersSerializer(member,data = request.data,partial=True)
                        if member_serializer.is_valid():
                            member_serializer.save()
                            return Response(member_serializer.data,status=status.HTTP_200_OK)
                        else:
                            return Response(member_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                else:
                    name = member.user.username
                    member.delete()
                    return Response({'message':f'Successfully deleted {name}'},status=status.HTTP_200_OK)
            else:
                return Response({'detail':'Missing member_id for update'},status=status.HTTP_400_BAD_REQUEST)




class TaskViews(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at']
    def get_serializer_class(self):
        if self.action == 'assignments':
            # if self.request.method == 'GET':
            #     return UserSerializer  # Explicitly return UserSerializer for GET requests
            return TaskAssignmentSerializer  # Use TaskAssignmentSerializer for other requests
        return TaskSerializer  # Default TaskSerializer
    
    def get_filterset_class(self):
        if self.action == 'assignments' and self.request.method == 'GET':
            return TaskAssignmentFilter
        return TasksFilter


    # def list(self, request, *args, **kwargs):
    #     return Response(status=status.HTTP_403_FORBIDDEN)  # Disable the get api/tasks/ endpoint
    
    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)  # Disable the post api/tasks/ endpoint
    
    @transaction.atomic()
    # task assignments (assign a task to a user url = api/tasks/task_id/assignments (retrive, post)/?assignee_id(patch, delete))
    @action(detail=True,methods=['post','get','patch','delete'],url_path='assignments(?:/(?P<assignee_id>[^/.]+))?')
    def assignments(self,request:dict,pk:None|str=None,assignee_id :None|str=None)-> Response[Any]:
        task_instance = self.get_object()
        print(f'{task_instance.project_teams = }')
        method=request.method
        try: TaskAssignment.objects.get(id=assignee_id) if assignee_id else None
        except TaskAssignment.DoesNotExist: return Response({'error':'assignee id is not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e: return Response({'error':str(e)},status=status.HTTP_404_NOT_FOUND)
        if method == 'GET':
            if assignee_id:
                try:
                    member = TaskAssignment.objects.get(id=assignee_id)
                except TaskAssignment.DoesNotExist: return Response({'error':'id is unassigned'},status=status.HTTP_404_NOT_FOUND)
                except Exception as e: return Response({'error':f'{e}'},status=status.HTTP_400_BAD_REQUEST)
                member_serializer = TaskAssignmentSerializer(members)
                return Response(member_serializer.data,status=status.HTTP_200_OK)
            try:
                members = TaskAssignment.objects.get(task=task_instance)
            except TaskAssignment.DoesNotExist:
                return Response({'Message':'Task is unassigned'},status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({'detail':str(e)},status=status.HTTP_400_BAD_REQUEST)
            else:
                member_serializer = TaskAssignmentSerializer(members)
            return Response(member_serializer.data,status=status.HTTP_200_OK)
        elif method == 'POST':
            data = deepcopy(request.data)
            user_id = data.get('user') or data.get('user_id')
            if task_instance.project_teams:
                try: inteam = TeamMembers.objects.get(team=task_instance.project_teams.team,user_id=user_id) 
                except TeamMembers.DoesNotExist: return Response({'error':'assignee is not in the right project team'},status=status.HTTP_404_NOT_FOUND) 
                except Exception as e: return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
                print(f'{inteam = }')
            else:
                data.setdefault('is_in_team',False)
            data.setdefault('task',pk)
            print(f'{data = }')
            assignee_serializer = TaskAssignmentSerializer(data=data)
            if assignee_serializer.is_valid():
                assignee_serializer.save()
                return Response(assignee_serializer.data,status=status.HTTP_201_CREATED)
            return Response(assignee_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        elif method in {'PATCH','DELETE'}:
            if not assignee_id:
                return Response({'detail':'needed assignee_id for patch and delete request'},status=status.HTTP_400_BAD_REQUEST)
            if method == 'PATCH':
                inteam = request.data.get('is_in_team')
                user_id = TaskAssignment.objects.filter(id=assignee_id).first()
                if inteam == True:
                    if not user_id:
                        return Response({'detail':'assignee id not found'},status=status.HTTP_404_NOT_FOUND)
                    if task_instance.project_teams:
                        try: inteam = TeamMembers.objects.get(team=task_instance.project_teams.team,user=user_id.user) 
                        except TeamMembers.DoesNotExist: return Response({'error':'assignee is not in the right project team'},status=status.HTTP_404_NOT_FOUND) 
                        except Exception as e: return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'detail':'is_in_team cannot be true for an individual user'},status=status.HTTP_400_BAD_REQUEST)
                elif inteam == False:
                    try: inteam = TeamMembers.objects.get(team=task_instance.project_teams.team,user=user_id.user) 
                    except TeamMembers.DoesNotExist: 
                        pass
                    except Exception as e: return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
                    else: return Response({'detail':'is_in_team cannot be false for an teamed user of the project'},status=status.HTTP_400_BAD_REQUEST)
                
                patch_serializer = TaskAssignmentSerializer(user_id,data=request.data,partial=True)

                if patch_serializer.is_valid():
                    patch_serializer.save()
                    return Response(request.data,status=status.HTTP_200_OK)
                return Response(patch_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    member = TaskAssignment.objects.get(pk=assignee_id)
                    member.delete()
                except TaskAssignment.DoesNotExist: return Response({'error':'assignee id not found in task assignment'},status=status.HTTP_404_NOT_FOUND)
                except Exception as e : return Response({'detail':str(e)},status=status.HTTP_404_NOT_FOUND)
                else: return Response({'message':f'{assignee_id} id is deleted successfully'},status=status.HTTP_200_OK)

class ProjectViews(viewsets.ModelViewSet):
    queryset = Projects.objects.all()
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'tasks__title', 'comments__text']  # Search in projects, tasks, and comments
    ordering_fields = ['created_at', 'name']  # Allow ordering by name or created_at
    def get_serializer_class(self):
        if self.action == 'assign':
            return ProjectTeamSerializer
        elif self.action == 'members':
            # if self.request.method == 'GET':
            #     ...
            return UserSerializer
        elif self.action == 'tasks':
            return TaskSerializer
        elif self.action == 'comments':
            return ProjectCommentSerializer
        return ProjectsSerializer
        # serializer_map = {'assign':ProjectTeamSerializer,'members':UserSerializer,'tasks':TaskSerializer,'comments':ProjectCommentSerializer}
        # return serializer_map.get(self.action,ProjectsSerializer)

    def get_filterset_class(self):
        if self.action == 'assign' and self.request.method == 'GET':
            return ProjectTeamFilter
        elif self.action == 'members' and self.request.method == 'GET':
            return UserFilter
        elif self.action == 'tasks' and self.request.method == 'GET':
            return TasksFilter
        elif self.action == 'comments' and self.request.method == 'GET':
            return ProjectCommentsFilter
        return ProjectFilter

    @transaction.atomic()
    @action(detail=True,methods=['post','patch'],url_path='assign(?:/(?P<team_id>[^/.]+))?')
    def assign(self,request,pk=None,team_id=''):
        instance = self.get_object()
        status_ = request.data.get('status','On Going')
        print(instance)
        team = request.data.get('team') or request.data.get('team_id')
        if request.method == 'POST':
            # here we use direct creation instead of validation serial cause we just adding the team already exist so it ok
            try:
                team = Team.objects.get(pk=team)
            except Team.DoesNotExist:
                return Response({'detail':'team id not found'},status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'detail':f'{e}'},status=status.HTTP_400_BAD_REQUEST)
            # get_or_create it returns a tuple of (object,bool) if created bool => true if get bool => false
            project_team, created = ProjectTeams.objects.get_or_create(project = instance,team=team,status = status_)
            if not created:
                return Response({'detail':'team already exists for this project'},status=status.HTTP_400_BAD_REQUEST)
            return Response(ProjectTeamSerializer(project_team).data,status=status.HTTP_201_CREATED)
        
        else:
            # patch req
            if team_id:
                try:
                    project_team = ProjectTeams.objects.get(project=instance,team=team_id)
                    print(f'{project_team = }')
                except ProjectTeams.DoesNotExist:
                    return Response({'detail':'team_id was not found'},status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    return Response({'detail':f'{e}'},status=status.HTTP_400_BAD_REQUEST)
                
                project_team_serializer = ProjectTeamSerializer(project_team,data=request.data,partial=True)

                if project_team_serializer.is_valid():
                    project_team_serializer.save()
                    print('is valid')
                    return Response(project_team_serializer.data,status=status.HTTP_200_OK)
                return Response(project_team_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail':'missing project team id'},status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True,methods=['get'])
    def team(self,request,pk=None):
        instance = self.get_object()
        '''hard way'''
        # teams = ProjectTeams.objects.filter(project=instance)
        # if teams:
        #     project_team_serializer = ProjectTeamSerializer(teams,many=True) 
        #     return Response(project_team_serializer.data,status=status.HTTP_200_OK)
        '''easy way (through serializer .team .projectteams_set(a reverse foreign key in projects model))'''
        project_serializer = ProjectsSerializer(instance)
        if project_serializer.data['team']:
            return Response(project_serializer.data['team'],status=status.HTTP_200_OK)
        return Response({'message':'no details to show'},status=status.HTTP_200_OK)
    

    # to filter out project handling team members (can be updated furthur)
    @action(detail=True,methods=['get'],url_path='members(?:/(?P<member_id>[^/.]+))?')
    def members(self,request,pk=None,member_id=None):
        project_instance = self.get_object()
        method = request.method
        if method == 'GET':
            project_serializer = ProjectsSerializer(project_instance)
            team_id=[teams.get('team') for teams in project_serializer.data['team']]
            print(team_id)
            members = TeamMembers.objects.filter(team__in=team_id)
            if members:
                if member_id:
                    try:
                        member = members.get(pk=member_id)
                        user = User.objects.filter(teams__user=member.user.id).first()
                    except Exception as e:
                        return Response({'detail':str(e)},status=status.HTTP_404_NOT_FOUND)
                    else:
                        user_serializer = UserSerializer(user)
                        return Response(user_serializer.data,status=status.HTTP_200_OK)
                member_serializer = TeamMembersSerializer(members,many=True)
                return Response(member_serializer.data,status=status.HTTP_200_OK)
            return Response({'message':'no members to list'},status=status.HTTP_204_NO_CONTENT)
        
    @transaction.atomic()
    @action(detail=True,methods=['get','post'])
    def tasks(self,request,pk=None):
        project_instance = self.get_object()
        if request.method == 'GET':
            tasks = Tasks.objects.filter(project=project_instance)
            if tasks:
                task_serializer = TaskSerializer(tasks,many=True)
                # this is to filter the team from the project response remove the team key
                datas = deepcopy(task_serializer.data)
                filtered_data = [
                            {**data, 'project_details': {key: value for key, value in data['project_details'].items() if key != 'team'}}
                            for data in datas
                        ]
                return Response(filtered_data,status=status.HTTP_200_OK)
            return Response({'message':f'{pk} no tasks to list'},status=status.HTTP_204_NO_CONTENT)
        else: # post req
            data = deepcopy(request.data)
            data.setdefault('project',pk)
            project_team_id = request.data.get('project_teams')
            if project_team_id:
                try:
                    project_team = ProjectTeams.objects.get(pk=project_team_id,project=project_instance,status='On Going')
                except ProjectTeams.DoesNotExist:
                    return Response({'detail':f'id {project_team_id} doesnt exist in db or the status might be completed'},status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    return Response({'detail':f'{e}'},status=status.HTTP_400_BAD_REQUEST)
            print(request.data)
            task_serializer = TaskSerializer(data=data)
            if task_serializer.is_valid():
                task_serializer.save()
                return Response(task_serializer.data,status=status.HTTP_201_CREATED)
            return Response(task_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    @transaction.atomic()
    @action(detail=True,methods=['post','get','delete'],url_path='comments(?:/(?P<comment_id>[^/.]+))?')
    def comments(self,request,pk=None,comment_id=None):
            project_instance = self.get_object()
            user = request.user 
            method = request.method
            if method == 'GET':
                if comment_id:
                    comment = ProjectComments.objects.filter(pk=comment_id).first()
                    if not comment: return Response({'error':'comment id is not found'},status=status.HTTP_404_NOT_FOUND)
                    return Response(ProjectCommentSerializer(comment).data,status=status.HTTP_200_OK)
                comments = ProjectComments.objects.filter(project=project_instance)
                if comments:
                    comments_serializer = self.get_serializer(comments,many=True)
                    return Response(comments_serializer.data,status=status.HTTP_200_OK)
                return Response({'message':'nothing there to list'},status=status.HTTP_200_OK)
            elif method == 'POST':
                print(f'{request.data = }')
                user_id = request.data.get('user') or request.data.get('user_id')
                # else: user_id = user.id
                data = deepcopy(request.data)
                data.setdefault('project',pk)
                if not user_id:
                    return Response({'detail':'missing user id key from request'},status=status.HTTP_400_BAD_REQUEST)
                # Check if the user belongs to a team assigned to this project
                # temp = ProjectTeams.objects.filter(project=project_instance).values_list("team", flat=True)
                # print(f'{temp = }')
                # team = TeamMembers.objects.filter(team__in=temp)
                # print(f'{team = }')
                # user_ = team.filter(user_id=user_id)
                # print(f'{user_ = }')
                # user_detail = User.objects.filter(id=user_id)
                # print(f'{user_detail = }')
                # print(f'{user_id = }')
                is_member = TeamMembers.objects.filter(
                    team__in=ProjectTeams.objects.filter(project=project_instance).values_list("team", flat=True),
                    user_id=user_id
                ).exists()      #here we used a subquery like thing 
                if not is_member:
                    return Response({'detail':'Only project team members can comment'},status=status.HTTP_400_BAD_REQUEST)
                comments_serializer = self.get_serializer(data=data)
                if comments_serializer.is_valid():
                    comments_serializer.save()
                    return Response(comments_serializer.data,status=status.HTTP_201_CREATED)
                return Response(comments_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            else:
                if not comment_id:
                    return Response({'detail':'delete request needs comment id'},status=status.HTTP_400_BAD_REQUEST)
                comment = ProjectComments.objects.filter(pk=comment_id,project=project_instance).first()
                if not comment:
                    return Response({'detail':'comment id not found in db'},status=status.HTTP_404_NOT_FOUND)
                comment.delete()
                return Response({'message':f'{comment_id} id was deleted successfully'},status=status.HTTP_204_NO_CONTENT)


class NotificationViews(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = '__all__'
    search_fields = ['message','user','is_read','notification_type']
    ordering = ['-created_at']  # Set the default ordering field

    def get_queryset(self):
        """Only show notifications for the logged-in user"""
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Block manual creation of notifications"""
        return Response({"detail": "You cannot create notifications manually."}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        """Block manual updates (except for marking as read)"""
        return Response({"detail": "Updating notifications is not allowed."}, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        """Block partial updates (except for marking as read)"""
        return Response({"detail": "Updating notifications is not allowed."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['POST'])
    def mark_as_read(self, request, pk=None):
        """Mark a single notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for the user"""
        self.get_queryset().update(is_read=True)
        return Response({"message": "All notifications marked as read"}, status=status.HTTP_200_OK)



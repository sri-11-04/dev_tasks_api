from rest_framework import serializers
from .models import User, Team, TeamMembers, Projects, Tasks, ProjectComments, Notification, ProjectTeams, TaskAssignment
from django.conf import settings

'''
serializers are not callable for the custom methods in the views to use them we have to explicitly serialize it using get_serialize(data=request.data)
'''

# User serializer
class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        exclude = ['groups','user_permissions']
        read_only_fields = ['created_at']
        # it is same as we defining a field's name in the model attribute's like default = True etc
        extra_kwargs = {
            'password':{'write_only':True},
            'user_permissions': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)
        
        if request:
            if not request.user.is_superuser:  # Check if the user is a superuser
                self.Meta.extra_kwargs.setdefault('is_active',{'read_only':True})  # Exclude fields for non-superusers
                self.Meta.extra_kwargs.setdefault('is_staff',{'read_only':True})  # Exclude fields for non-superusers
                self.Meta.extra_kwargs.setdefault('is_superuser',{'read_only':True})  # Exclude fields for non-superusers
                self.Meta.extra_kwargs.setdefault('role',{'read_only':True})  # Exclude fields for non-superusers
            else:
                if self.Meta.extra_kwargs.get('is_superuser'):
                    self.Meta.extra_kwargs.pop('is_active')
                    self.Meta.extra_kwargs.pop('is_staff')
                    self.Meta.extra_kwargs.pop('is_superuser')
                    self.Meta.extra_kwargs.pop('role')
                    


        # self.Meta.read_only_fields = list(set(self.Meta.exclude))  # Remove duplicates

    # password validation
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def get_avatar_url(self, obj):
        if obj.avatar:
            return f"{settings.MEDIA_URL}{obj.avatar}"
        return None

    # this is the method that will be called when is_valid() is called in the views if we use custom user manager we can modify it as in the bellow code
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)
    
    # this is the method that will be called when is_valid() is called in the views on put or patch method
    def update(self, instance, validated_data):
        # Check if the password is being updated and hash it using set_password
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            validated_data.pop('password')  # Remove the password from validated_data to avoid conflict

        # Update fields on the instance
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
# Team serializer
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['created_at']

# Team members serializer
class TeamMembersSerializer(serializers.ModelSerializer):
    '''for the issue with adding the team id and user id'''
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Accept user ID
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())  # Accept team ID
    class Meta:
        model = TeamMembers
        fields = '__all__'

# ProjectTeams serializer
class ProjectTeamSerializer(serializers.ModelSerializer):
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())  #to overcome uuid issue
    class Meta:
        model = ProjectTeams
        fields = '__all__'
        read_only_fields = ['created_at','updated_by']

# Projects serializer
class ProjectsSerializer(serializers.ModelSerializer):
    # if ProjectTeamSerializer didnt give data it will not show in the response
    team = ProjectTeamSerializer(many=True,read_only=True,source='projectteams_set')
    class Meta:
        model = Projects
        fields = '__all__'
        read_only_fields = ['created_at']


# Tasks serializer
class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Projects.objects.all(), write_only=True)
    project_details = ProjectsSerializer(source='project', read_only=True)  # Show project details
    project_teams = serializers.PrimaryKeyRelatedField(queryset=ProjectTeams.objects.all(), allow_null=True, required=False, write_only=True)
    project_team_details = TeamSerializer(source='team', read_only=True)  # Show team details

    class Meta:
        model = Tasks
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# Tasks Assagnment Serializer
class TaskAssignmentSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Tasks.objects.all(), write_only=True)
    task_details = TaskSerializer(source='task', read_only=True)  # Show task details
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    user_details = UserSerializer(source='user', read_only=True)  # Show user details

    class Meta:
        model = TaskAssignment
        fields = '__all__'



# # Task comments serializer
# class TaskCommentsSerializer(serializers.ModelSerializer):
#     task = serializers.PrimaryKeyRelatedField(queryset=Tasks.objects.all(), write_only=True)
#     task_title = serializers.StringRelatedField(source='task', read_only=True)  # Show task title
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
#     user_details = UserSerializer(source='user', read_only=True)  # Show user details

#     class Meta:
#         model = TaskComments
#         fields = '__all__'
#         read_only_fields = ['created_at']

# Project comments
class ProjectCommentSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField() # to return user name instead of id
    class Meta:
        model = ProjectComments
        fields = '__all__'
        read_only_fields = ['id','created_at']


# Notification serializer
class NotificationSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)  # Show user details

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at','id']




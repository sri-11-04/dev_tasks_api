from django_filters import FilterSet
from .models import User,TaskAssignment,Tasks,Team,TeamMembers,ProjectComments,Projects,ProjectTeams,Notification

class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = ['username','id','email','bio','is_active','is_staff','is_superuser','last_login','created_at']

class TaskAssignmentFilter(FilterSet):
    class Meta:
        model = TaskAssignment
        fields = '__all__'

class TasksFilter(FilterSet):
    class Meta:
        model = Tasks
        fields = '__all__'

class TeamFilter(FilterSet):
    class Meta:
        model = Team
        fields = '__all__'

class TeamMembersFilter(FilterSet):
    class Meta:
        model = TeamMembers
        fields = '__all__'

class ProjectCommentsFilter(FilterSet):
    class Meta:
        model = ProjectComments
        fields = '__all__'

class ProjectFilter(FilterSet):
    class Meta:
        model = Projects
        fields = '__all__'

class ProjectTeamFilter(FilterSet):
    class Meta:
        model = ProjectTeams
        fields = '__all__'

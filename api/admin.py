from django.contrib import admin
from .models import User,ProjectComments,Tasks,Team,TeamMembers,Notification,Projects,ProjectTeams

# Register your models here.


admin.site.register(User)
admin.site.register(ProjectComments)
admin.site.register(Tasks)
admin.site.register(Team)
admin.site.register(TeamMembers)
admin.site.register(Projects)
admin.site.register(Notification)
admin.site.register(ProjectTeams)
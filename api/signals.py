from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import ProjectTeams, Tasks, ProjectComments, TeamMembers
from .tasks import create_notification

@receiver(post_save, sender=ProjectTeams)
def notify_team_added(sender, instance, created, **kwargs):
    """Notify all team members when their team is added to a project."""
    print('inside method')
    if created:
        print('inside created')
        message = f"Your team '{instance.team.name}' has been added to the project '{instance.project.name}'."
        
        # Notify all members in the team
        team_members = TeamMembers.objects.filter(team=instance.team).values_list("user_id", flat=True)
        for member_id in team_members:
            create_notification.delay(member_id, "project", message)

@receiver(post_save, sender=Tasks)
def notify_task_assigned(sender, instance, created, **kwargs):
    """Notify all team members when a new task is assigned to their team."""
    print('inside method')
    if created and instance.project_teams:
        print('inside created')
        message = f"A new task '{instance.title}' has been assigned to your team in project '{instance.project.name}'."
        
        # Notify all team members
        team_members = TeamMembers.objects.filter(team=instance.project_teams.team).values_list("user_id", flat=True)
        for member_id in team_members:
            create_notification.delay(member_id, "task", message)

@receiver(post_save, sender=ProjectComments)
def notify_project_comments(sender, instance, created, **kwargs):
    """Notify all project team members when someone comments on the project."""
    print('inside method')
    if created:
        print('inside created')
        project_teams = ProjectTeams.objects.filter(project=instance.project)

        # Get all team members from the project teams
        team_members = TeamMembers.objects.filter(team__in=project_teams.values_list("team", flat=True)).values_list("user_id", flat=True)
        
        message = f"{instance.user.username} commented on project '{instance.project.name}': {instance.text[:50]}..."
        for member_id in team_members:
            create_notification.delay(member_id, "comment", message)

@receiver(post_save, sender=TeamMembers)
def notify_added_to_team(sender, instance, created, **kwargs):
    """Notify users when they are added to a team."""
    print('inside method')
    if created:
        print('inside created')
        message = f"You have been added to the team '{instance.team.name}'."
        create_notification.delay(instance.user.id, "team", message)

@receiver(post_delete, sender = TeamMembers)
def notify_on_delete(sender, instance, **kwargs):
    """notify the user when they been removed from the team"""
    print('on delete from team')

    message = f'hey! {instance.user.username} you\'ve been removed from the {instance.team.name} team :( '
    create_notification.delay(instance.user.id,'delete',message) 

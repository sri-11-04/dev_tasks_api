from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import os


def default_time():
    return (timezone.now() + relativedelta(months=1)).date()

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role','Admin')
        return self.create_user(email, password, **extra_fields)

def user_avatar_path(instance, filename):
    ext = filename.split('.')[-1]  # Get the file extension
    filename = f'avatar_{instance.id}.{ext}'  # Example: avatar_c31f0c36-52d9-4f52-8c98-123abc.jpg
    return os.path.join('avatars/', filename)

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=False)
    username = models.CharField(max_length=255, unique=True, null=False)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Team Lead', 'Team Lead'),
        ('Developer', 'Developer'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Developer')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

# Team Model
class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField()
    team_lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="leading_teams")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Team Members Model
class TeamMembers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='teams')
    ROLE_CHOICES = [
        ('Team Lead', 'Team Lead'),
        ('Developer', 'Developer'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Developer')
    
    class Meta:
        unique_together = ("user", "team")  # Ensure a user cannot be added twice to the same team  => both are field name 
    def __str__(self):
        return f'{self.user.username} from {self.team.name} team'

# Projects Model
class Projects(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

# ProjectTeams Model
class ProjectTeams(models.Model):
    project = models.ForeignKey(Projects,on_delete=models.CASCADE)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    status = models.CharField(max_length=20,choices=[('On Going','On Going'),('Completed', 'Completed')],default='On Going')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project','team')    #prevent duplicate team in a project

    def __str__(self):
        return f'{self.status} {self.project.name} project by {self.team.name} team'

# Tasks Model
class Tasks(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE,related_name="tasks")
    project_teams = models.ForeignKey(ProjectTeams,on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='In Progress')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low')
    due_date = models.DateField(default=default_time)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Project => {self.project.name} | Task => {self.title}'

# Task Assignment model
class TaskAssignment(models.Model):
    task = models.OneToOneField(Tasks,on_delete=models.CASCADE) # one task for one user
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="task_assignments")    #user can have multiple tasks
    is_in_team = models.BooleanField(default=True)


# project comments model
class ProjectComments(models.Model):
    project = models.ForeignKey(Projects,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.title}"

# Notification Model
class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    NOTIFICATION_TYPES = [
        ("team", "Added to a Team"),
        ("project", "Added to a Project"),
        ("task", "Assigned a Task"),
        ("comment", "Project Comment"),
        ('delete',"Removed from a Team")
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='notifications')
    notification_type = models.CharField(max_length=20,choices=NOTIFICATION_TYPES)
    message = models.TextField(null=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message[:50]}'



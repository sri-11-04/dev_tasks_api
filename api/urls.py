from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from . import views
from django.urls import path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('auth',views.UserViews,basename='auth')
router.register('teams',viewset=views.TeamViews,basename='teams')
router.register('projects',viewset=views.ProjectViews,basename='projects')
router.register('tasks',viewset=views.TaskViews,basename='tasks')
router.register('notifications',viewset=views.NotificationViews,basename='notification')


urlpatterns = [
    path('auth/login/',TokenObtainPairView.as_view(),name='token-obtain'),
    path('auth/refresh/',TokenRefreshView.as_view(),name='refresh-token'),
] + router.urls

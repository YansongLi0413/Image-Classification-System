from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('me/', views.UserInfoView.as_view(), name='user-info'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('refresh/', views.RefreshTokenView.as_view(), name='refresh-token'),
]

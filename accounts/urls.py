# accounts/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),

    # Password change
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/password_change.html',
             success_url='/password-change/done/'
         ),
         name='password_change'),

    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         ),
         name='password_change_done'),
]
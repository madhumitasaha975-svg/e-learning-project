# courses/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.create_course, name='create_course'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:pk>/rate/', views.rate_course, name='rate_course'),
    path('<int:pk>/manage/', views.manage_course, name='manage_course'),
    path('<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('<int:course_pk>/lessons/<int:lesson_pk>/', views.lesson_detail, name='lesson_detail'),
    path('<int:course_pk>/lessons/<int:lesson_pk>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('<int:course_pk>/lessons/<int:lesson_pk>/delete/', views.delete_lesson, name='delete_lesson'),
    path('<int:pk>/certificate/', views.course_certificate, name='course_certificate'),
]
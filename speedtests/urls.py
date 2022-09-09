from django.urls import path

from . import views


app_name = 'speedtests'
urlpatterns = [
    path('result/', views.ResultView.as_view()),
    path('machine/', views.MachineView.as_view()),
    path('machine_tasks/', views.MachineTasksView.as_view()),
    path('machine_task/', views.MachineTaskView.as_view()),
    path('server/', views.ServerAPIView.as_view()),
    path('server_list/', views.ServerListAPIView.as_view()),
    path('search/', views.SearchAPIView.as_view()),
    path('signup/', views.SignUpView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('my/', views.MyView.as_view()),
]
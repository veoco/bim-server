from django.urls import path

from speedtests import views as speedtest_views

urlpatterns = [
    path('api/result/', speedtest_views.ResultView.as_view()),
    path('api/machine/', speedtest_views.MachineView.as_view()),
    path('api/machine_tasks/', speedtest_views.MachineTasksView.as_view()),
    path('api/machine_task/', speedtest_views.MachineTaskView.as_view()),
    path('api/server/', speedtest_views.ServerAPIView.as_view()),
    path('api/server_list/', speedtest_views.ServerListAPIView.as_view()),
    path('api/search/', speedtest_views.SearchAPIView.as_view()),
    path('api/signup/', speedtest_views.SignUpView.as_view()),
    path('api/login/', speedtest_views.LoginView.as_view()),
    path('api/logout/', speedtest_views.LogoutView.as_view()),
    path('api/my/', speedtest_views.MyView.as_view()),
]

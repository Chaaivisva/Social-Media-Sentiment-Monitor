from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/sentiment-data/', views.get_sentiment_data, name='api-sentiment-data'),
    path('login/', auth_views.LoginView.as_view(template_name='social_analyzer/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
     path('register/', views.register, name='register'),
    path('reports/', views.view_reports, name='view-reports'),
    path('reports/save/', views.save_report, name='save-report'),
    path('reports/load/<int:report_id>/', views.load_report, name='load-report'),
]
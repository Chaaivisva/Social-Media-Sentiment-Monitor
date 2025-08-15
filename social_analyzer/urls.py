from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/sentiment-data/', views.get_sentiment_data, name='api-sentiment-data'),
]
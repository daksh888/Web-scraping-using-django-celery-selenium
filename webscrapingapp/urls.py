from django.urls import path
from .views import CoinMarketCap

urlpatterns = [
    path('api/taskmanager/start_scraping/',CoinMarketCap.as_view()),
    path('api/taskmanager/scraping_status/<str:job_id>/',CoinMarketCap.as_view()),
    
]

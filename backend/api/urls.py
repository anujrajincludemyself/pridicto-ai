from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('routes/search/', views.search_routes, name='search_routes'),
    path('routes/ai-search/', views.ai_search, name='ai_search'),
    path('stations/search/', views.station_search, name='station_search'),
    path('train/status/', views.train_status, name='train_status'),
    path('train/seat-availability/', views.seat_availability, name='seat_availability'),
    path('routes/popular/', views.popular_routes, name='popular_routes'),
]

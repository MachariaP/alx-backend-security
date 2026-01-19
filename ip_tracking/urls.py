from django.urls import path
from . import views

app_name = 'ip_tracking'

urlpatterns = [
    path('login/', views.anonymous_login, name='anonymous_login'),
    path('action/', views.authenticated_action, name='authenticated_action'),
    path('sensitive/', views.sensitive_endpoint, name='sensitive_endpoint'),
]

from django.urls import path

from .views import dashboard_redirect_view, home_view

app_name = 'core'

urlpatterns = [
    path('', home_view, name='home'),
    path('dashboard/', dashboard_redirect_view, name='dashboard_redirect'),
]

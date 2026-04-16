from django.urls import path

from .views import make_payment, payment_list

app_name = 'payments'

urlpatterns = [
    path('', payment_list, name='payment_list'),
    path('<int:pk>/pay/', make_payment, name='make_payment'),
]

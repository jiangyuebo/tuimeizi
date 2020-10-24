from django.urls import path
from . import views

app_name = "mypayment"
urlpatterns = [
    path('mypayment', views.my_payment, name="mypayment"),
]

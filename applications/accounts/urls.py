from django.urls import path

from applications.accounts.views import Dashboard

urlpatterns = [
    path('', Dashboard.as_view(), name="dashboard"),

]
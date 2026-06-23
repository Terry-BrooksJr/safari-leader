from django.urls import path

from applications.accounts.views import Dashboard, EnrollmentIntakeView

urlpatterns = [
    path("", Dashboard.as_view(), name="dashboard"),
    path("enroll/", EnrollmentIntakeView.as_view(), name="enroll"),
]

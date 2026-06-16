from django.urls import path

from applications.enrollment.views import EnrollmentDetailView, EnrollmentList

urlpatterns = [
    path(
        "enrollment/<int:pk>", EnrollmentDetailView.as_view(), name="enrollment-detail"
    ),
    path("", EnrollmentList.as_view(), name="enrollment-list"),
]

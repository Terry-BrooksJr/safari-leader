from django.urls import path

from applications.children.views import ChildDetailView, ChildrenList

urlpatterns = [
    path('', ChildrenList.as_view(),name="children-list"),
    path("child/<int:pk>", ChildDetailView.as_view(), name="child-detail")
]
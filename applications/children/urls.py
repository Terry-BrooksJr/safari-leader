from django.urls import path
from applications.children.views import ChildrenList, ChildDetailView
urlpatterns = [
    path('', ChildrenList.as_view(),name="children-list"),
    path("child/<int:pk>", ChildDetailView.as_view(), name="child-detail")
]
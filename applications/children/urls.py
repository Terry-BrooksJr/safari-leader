from django.urls import path
from applications.children.views import ChildrenList
urlpatterns = [
    path('children/', ChildrenList.as_view(), name="children_list"),

]
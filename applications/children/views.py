from django.shortcuts import render
from applications.children.models import Child
from django.views.generic import TemplateView


# Create your views here.

class ChildrenList(TemplateView):
    template_name = 'children/children_list.html'
    extra_context = {"children":Child.objects.all()}
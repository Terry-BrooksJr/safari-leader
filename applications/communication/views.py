from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Announcement, Notification

class AnnoucementsList(ListView):
    pass

class NotificationsList(ListView):
    pass

class AnnoucementDetails(DetailView):
    pass

class NotificationDetails(DetailView):
    pass

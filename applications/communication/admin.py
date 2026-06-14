from django.contrib import admin
from applications.communication.models import Announcement, Notification, Message

models = {Announcement, Notification, Message}

for model in models: 
    admin.site.register(model)
# Register your models here.
from django.contrib import admin

from applications.documents.models import Document

models = {Document}

for model in models:
    admin.site.register(model)

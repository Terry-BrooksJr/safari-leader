from django.contrib import admin
from applications.accounts.models import User, Role, RoleAssignment

models = {User, RoleAssignment, Role}

for model in models:
    admin.site.register(model)
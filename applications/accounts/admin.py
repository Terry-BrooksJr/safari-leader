from django.contrib import admin

from applications.accounts.models import Role, RoleAssignment, User

models = {User, RoleAssignment, Role}

for model in models:
    admin.site.register(model)

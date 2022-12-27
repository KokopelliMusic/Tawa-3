from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, AccessToken

admin.site.register(User)
admin.site.unregister(Group)
admin.site.register(AccessToken)
from django.contrib import admin

from friends.models import Profile, FriendRequest

admin.site.register(Profile)
admin.site.register(FriendRequest)
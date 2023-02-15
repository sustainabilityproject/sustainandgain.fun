from django.urls import path
from accounts.views import RegisterView, profile, friends_list, add_friend, remove_friend, accept_friend_request, decline_friend_request, cancel_friend_request
import os   

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", profile ,name="profile"),
    path('friends/', friends_list, name='friends_list'),
    path('add-friend/', add_friend, name='add_friend'),
    path('remove-friend/<str:username>/', remove_friend, name='remove_friend'),
    path('accept-friend-request/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('decline-friend-request/<int:request_id>/', decline_friend_request, name='decline_friend_request'),
    path('cancel-friend-request/<int:friend_request_id>/', cancel_friend_request, name='cancel_friend_request'),
]



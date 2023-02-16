from django.urls import path

from friends.views import profile, friends_list, add_friend, remove_friend, accept_friend_request, \
    decline_friend_request, cancel_friend_request

urlpatterns = [
    path("profile/", profile, name="profile"),
    path('', friends_list, name='friends_list'),
    path('add', add_friend, name='add_friend'),
    path('remove/<str:username>/', remove_friend, name='remove_friend'),
    path('accept/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('decline/<int:request_id>/', decline_friend_request, name='decline_friend_request'),
    path('cancel/<int:friend_request_id>/', cancel_friend_request, name='cancel_friend_request'),
]

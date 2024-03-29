from django.urls import path

from friends.views import ProfileView, \
    FriendsListView, RemoveFriendView, CancelFriendRequestView, AddFriendView, \
    AcceptFriendRequestView, DeclineFriendRequestView, UpdateProfileView, \
    ProfileSearchView

app_name = "friends"
urlpatterns = [
    path('', FriendsListView.as_view(), name='list'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('add/', AddFriendView.as_view(), name='add'),
    path('remove/<str:username>/', RemoveFriendView.as_view(), name='remove'),
    path('accept/<int:request_id>/', AcceptFriendRequestView.as_view(), name='accept_request'),
    path('decline/<int:pk>/', DeclineFriendRequestView.as_view(), name='decline_request'),
    path('cancel/<int:friend_request_id>/', CancelFriendRequestView.as_view(), name='cancel_request'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('search/', ProfileSearchView.as_view(), name='profile_search'),
]

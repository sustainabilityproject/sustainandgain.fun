from django.urls import path

from leagues.views import LeaguesListView, LeagueDetailView, JoinLeagueView, LeaveLeagueView, DeleteLeagueView, \
    InviteMemberView, RemoveMemberView, PendingMembersView, CreateLeagueView, EditLeagueView, PromoteMemberView, \
    DemoteMemberView

app_name = "leagues"
urlpatterns = [
    path('', LeaguesListView.as_view(), name='list'),
    path('<int:pk>/', LeagueDetailView.as_view(), name='detail'),
    path('<int:pk>/join/', JoinLeagueView.as_view(), name='join'),
    path('<int:pk>/leave/', LeaveLeagueView.as_view(), name='leave'),
    path('create/', CreateLeagueView.as_view(), name='create'),

    # League admin only
    path('<int:pk>/edit/', EditLeagueView.as_view(), name='edit'),
    path('<int:pk>/delete/', DeleteLeagueView.as_view(), name='delete'),
    path('<int:pk>/invite/', InviteMemberView.as_view(), name='invite'),
    path('<int:pk>/remove/<str:username>/', RemoveMemberView.as_view(), name='remove'),
    path('<int:pk>/pending/', PendingMembersView.as_view(), name='pending'),
    path('<int:pk>/promote/<str:username>/', PromoteMemberView.as_view(), name='promote'),
    path('<int:pk>/demote/<str:username>/', DemoteMemberView.as_view(), name='demote'),
]

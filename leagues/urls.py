from django.urls import path

from leagues.views import LeaguesListView, LeagueDetailView, JoinLeagueView, LeaveLeagueView, DeleteLeagueView

app_name = "leagues"
urlpatterns = [
    path('', LeaguesListView.as_view(), name='list'),
    path('<int:pk>/', LeagueDetailView.as_view(), name='detail'),
    path('<int:pk>/join/', JoinLeagueView.as_view(), name='join'),
    path('<int:pk>/leave/', LeaveLeagueView.as_view(), name='leave'),
    path('<int:pk>/delete/', DeleteLeagueView.as_view(), name='delete')
]

from django.urls import path

from leagues.views import LeaguesListView, LeagueDetailView

app_name = "leagues"
urlpatterns = [
    path('', LeaguesListView.as_view(), name='list'),
    path('<int:pk>/', LeagueDetailView.as_view(), name='detail'),
]
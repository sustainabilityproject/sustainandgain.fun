from django.urls import path

from leagues.views import LeaguesListView

app_name = "leagues"
urlpatterns = [
    path('', LeaguesListView.as_view(), name='list'),
]
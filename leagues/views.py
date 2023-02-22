from django.views.generic import ListView

from leagues.models import League


class LeaguesListView(ListView):
    model = League
    context_object_name = 'leagues'

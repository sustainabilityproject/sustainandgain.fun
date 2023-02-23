from django.views.generic import ListView, DetailView

from leagues.models import League


class LeaguesListView(ListView):
    model = League
    context_object_name = 'leagues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_leagues'] = self.request.user.profile.leagues.all()
            context['leagues'] = context['leagues'].exclude(id__in=context['user_leagues'])
        return context


class LeagueDetailView(DetailView):
    model = League
    context_object_name = 'league'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.ranked_members()
        return context


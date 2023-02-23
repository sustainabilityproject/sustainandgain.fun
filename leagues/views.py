from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, UpdateView, DeleteView

from leagues.models import League, LeagueMember


class LeaguesListView(ListView):
    model = League
    context_object_name = 'leagues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_leagues'] = self.request.user.profile.league_set.all()
            context['leagues'] = context['leagues'].exclude(id__in=context['user_leagues'])
        return context


class LeagueDetailView(DetailView):
    model = League
    context_object_name = 'league'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.get_ranked_members()
        context['is_member'] = False
        context['is_pending'] = False
        context['is_invited'] = False
        context['admin'] = False

        if self.request.user.is_authenticated:
            try:
                member = LeagueMember.objects.get(league=self.object, profile=self.request.user.profile)
                if member.status == 'joined':
                    context['is_member'] = True
                elif member.status == 'pending':
                    context['is_pending'] = True
                elif member.status == 'invited':
                    context['is_invited'] = True
                if member.role == 'admin':
                    context['admin'] = True
                    context['invited_members'] = self.object.get_invited_members()
                    context['pending_members'] = self.object.get_pending_members()
            except LeagueMember.DoesNotExist:
                context['is_member'] = False
        return context


class JoinLeagueView(LoginRequiredMixin, UpdateView):
    model = League
    fields = []

    def get(self, request, *args, **kwargs):
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        league = self.get_object()
        # Check if the user is already a member of the league
        if request.user.profile in league.members.all():
            messages.info(request, 'You are already a member of this league.')
            return redirect('leagues:detail', pk=league.pk)

        # Add the user to the league
        league.members.add(request.user.profile)

        member = LeagueMember.objects.get(league=league, profile=request.user.profile)

        # Check if the league is invite only
        if league.invite_only:
            # If the user hasn't been invited, change their status to pending
            if not LeagueMember.objects.filter(league=league, profile=request.user.profile, status='invited').exists():
                messages.success(request, f'You have requested to join {league.name}')
                return redirect('leagues:detail', pk=league.pk)

        member.status = 'joined'
        member.save()
        messages.info(request, f'You have joined {league.name}')
        return redirect('leagues:detail', pk=league.pk)


class LeaveLeagueView(LoginRequiredMixin, UpdateView):
    model = League
    fields = []

    def get(self, request, *args, **kwargs):
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        league = self.get_object()

        # Check if the user is not a member of the league
        if request.user.profile not in league.members.all():
            messages.info(request, 'You are not a member of this league.')
            return redirect('leagues:detail', pk=league.pk)

        # Can't leave a league if the user is the only admin
        member = LeagueMember.objects.get(league=league, profile=request.user.profile)
        if member.role == 'admin' and LeagueMember.objects.filter(Q(league=league) and Q(role='admin')).count() == 1:
            messages.warning(request, 'You are the only admin of this league. You cannot leave.')
            return redirect('leagues:detail', pk=league.pk)

        # Remove the user from the league
        league.members.remove(request.user.profile)

        messages.info(request, f'You have left {league.name}')
        return redirect('leagues:detail', pk=league.pk)


class DeleteLeagueView(LoginRequiredMixin, DeleteView):
    """
    If the user is an admin, they can delete the league
    """
    model = League
    success_url = '/leagues/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Check if the user is an admin of the league
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)


from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView

from friends.models import Profile
from leagues.forms import InviteMemberForm
from leagues.models import League, LeagueMember


class LeaguesListView(ListView):
    """
    If user not logged in, show all public leagues.
    If user logged in, show all public leagues, leagues the user is a member of, leagues the user has been invited to,
    and leagues the user has requested to join.
    """
    model = League
    context_object_name = 'leagues'

    def get_queryset(self):
        return League.objects.filter(visibility='public')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_leagues'] = League.objects.filter(leaguemember__profile=self.request.user.profile,
                                                            leaguemember__status='joined')
            context['invited_leagues'] = League.objects.filter(leaguemember__profile=self.request.user.profile,
                                                               leaguemember__status='invited')
            context['pending_leagues'] = League.objects.filter(leaguemember__profile=self.request.user.profile,
                                                               leaguemember__status='pending')
            context['leagues'] = context['leagues'].exclude(
                Q(pk__in=context['user_leagues']) | Q(pk__in=context['invited_leagues']) | Q(
                    pk__in=context['pending_leagues']))
        return context


class LeagueDetailView(DetailView):
    """
    Show the details of a league.
    If the league is public, show title, description and members.
    If the league is private, only show title and description.
    If the user is a member of the league, show the members.
    """
    model = League
    context_object_name = 'league'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.get_ranked_members()
        context['is_member'] = False
        context['is_pending'] = False
        context['is_invited'] = False
        context['is_public'] = self.object.visibility == 'public'
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
                    context['pending_members'] = self.object.get_pending_members()
            except LeagueMember.DoesNotExist:
                context['is_member'] = False
        return context


class JoinLeagueView(LoginRequiredMixin, UpdateView):
    """
    If the league is public, add the user to the league.
    If the league is private, add the user to the league if they have been invited.
    If the league is private and the user has not been invited, change their status to pending.
    """
    model = League
    fields = []

    def get(self, request, *args, **kwargs):
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        league = self.get_object()

        if request.user.profile in league.get_members():
            messages.info(request, 'You are already a member of this league.')
            return redirect('leagues:detail', pk=league.pk)

        if league.invite_only:
            # If the user hasn't been invited, change their status to pending
            if not LeagueMember.objects.filter(league=league, profile=request.user.profile, status='invited').exists():
                member, created = LeagueMember.objects.get_or_create(league=league, profile=request.user.profile)
                member.status = 'pending'
                member.save()
                messages.success(request, f'You have requested to join {league.name}')
                return redirect('leagues:detail', pk=league.pk)

        # If the user has been invited or the league is public, add them to the league
        member, created = LeagueMember.objects.get_or_create(league=league, profile=request.user.profile)
        member.status = 'joined'
        member.save()
        messages.success(request, f'You have joined {league.name}')
        return redirect('leagues:detail', pk=league.pk)


class LeaveLeagueView(LoginRequiredMixin, UpdateView):
    """
    A user can leave a league.
    """
    model = League
    fields = []

    def get(self, request, *args, **kwargs):
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        league = self.get_object()

        if request.user.profile not in league.members.all():
            messages.info(request, 'You are not a member of this league.')
            return redirect('leagues:detail', pk=league.pk)

        # Can't leave a league if the user is the only admin
        member = LeagueMember.objects.get(league=league, profile=request.user.profile)
        if member.role == 'admin' and LeagueMember.objects.filter(Q(league=league) and Q(role='admin')).count() == 1:
            messages.error(request, 'You are the only admin of this league. You cannot leave.')
            return redirect('leagues:detail', pk=league.pk)

        # If the user was invited by an admin, decline the invitation
        if member.status == 'invited':
            league.members.remove(request.user.profile)
            messages.success(request, f'You have declined the invitation to {league.name}')
            return redirect('leagues:detail', pk=league.pk)

        # If the user had requested to join the league, remove their request
        if member.status == 'pending':
            league.members.remove(request.user.profile)
            messages.success(request, f'You have removed your request to join {league.name}')
            return redirect('leagues:detail', pk=league.pk)
        else:
            league.members.remove(request.user.profile)
            messages.success(request, f'You have left {league.name}')
            return redirect('leagues:detail', pk=league.pk)


class DeleteLeagueView(LoginRequiredMixin, DeleteView):
    """
    If the user is an admin, they can delete the league
    """
    model = League
    success_url = reverse_lazy('leagues:list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Check if the user is an admin of the league
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)


class InviteMemberView(LoginRequiredMixin, UpdateView):
    """
    If the user is an admin, they can invite a user to the league
    """
    template_name = 'leagues/league_invite.html'
    model = League
    form_class = InviteMemberForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Check if the user is an admin of the league
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invited_members'] = self.object.get_invited_members()
        return context

    def get_success_url(self):
        return reverse_lazy('leagues:invite', kwargs={'pk': self.get_object().pk})

    def form_valid(self, form):
        profile = Profile.objects.get(user__username=form.cleaned_data['username'])
        # If the user had requested to join the league, add them to the league
        if LeagueMember.objects.filter(league=self.get_object(), profile=profile, status='pending').exists():
            member = LeagueMember.objects.get(league=self.get_object(), profile=profile)
            member.status = 'joined'
            member.save()
            messages.success(self.request, f'{profile.user.username} has joined {self.get_object().name}')
            return redirect('leagues:pending', pk=self.get_object().pk)
        else:
            member = LeagueMember.objects.create(league=self.get_object(), profile=profile)
            member.status = 'invited'
            member.save()
            messages.success(self.request, f'{profile.user.username} has been invited to {self.get_object().name}')
            return super().form_valid(form)


class RemoveMemberView(LoginRequiredMixin, UpdateView):
    """
    If the user is an admin, they can remove a user from the league
    """
    model = League

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        league = self.get_object()
        member = get_object_or_404(LeagueMember, league=league, profile__user__username=kwargs['username'])
        # Can't remove yourself
        if member.profile == request.user.profile:
            messages.error(request, 'You cannot remove yourself from the league.')
            return redirect('leagues:detail', pk=league.pk)
        member.delete()
        messages.success(request, f'{member.profile.user.username} has been removed from {league.name}')
        return redirect('leagues:detail', pk=league.pk)


class PendingMembersView(LoginRequiredMixin, DetailView):
    """
    If the user is an admin, they can view the members who have requested to join the league
    """
    model = League
    template_name = 'leagues/league_pending.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        # If there are no pending members, redirect to the league detail page
        if not obj.get_pending_members():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_members'] = self.object.get_pending_members()
        return context

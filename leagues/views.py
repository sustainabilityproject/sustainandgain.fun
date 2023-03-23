from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView

from friends.models import Profile
from leagues.forms import InviteMemberForm, CreateLeagueForm, EditLeagueForm
from leagues.models import League, LeagueMember


class LeaguesListView(ListView):
    """
    If user not logged in, show all public leagues.
    If user logged in, show all public leagues, leagues the user is a member of, leagues the user has been invited to,
    and leagues the user has requested to join.

    Attributes:
        model (League): The thing being displayed.
        context_object_name (str): What this is called in the template.

    Methods:
        get_queryset(self): Return list of public leagues.
        get_context_data(self, **kwargs): Returns all leagues, the leagues they have been invited to,
            and their pending leagues.
    """
    model = League
    context_object_name = 'leagues'

    def get_queryset(self):
        """
        Return list of public leagues.

        Returns:
            League.objects: Public leagues.
        """
        return League.objects.filter(visibility='public')

    def get_context_data(self, **kwargs):
        """
        Returns all leagues, the leagues they have been invited to, and their pending leagues.

        Returns:
            context (dict[str, League]): user leagues, invited leagues, pending leagues, leagues.
        """
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

    Attributes:
        model (League): The thing being displayed.
        context_object_name (str): What this is called in the template.

    Methods:
        get_context_data(self, **kwargs): Return the details of a league.
    """
    model = League
    context_object_name = 'league'

    def get_context_data(self, **kwargs):
        """
        Return the details of a league.
        If the league is public, return title, description and members.
        If the league is private, only return title and description.
        If the user is a member of the league, return the members.

        Returns:
            context (dict[str, Any]): The details of the league.
        """
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

    Attributes:
        model (League): The league being displayed.
        fields (list): The fields to be displayed.

    Methods:
        get(self, request, *args, **kwargs): 
        post(self, request, *args, **kwargs): Join the league.
    """
    model = League
    fields = []

    def get(self, request, *args, **kwargs):
        """
        Redirect to the league detail page.

        Returns:
            redirect: Redirects to the league detail page.
        """
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        """
        Join the league.

        Returns:
            redirect: Redirects to the league detail page.
        """
        league = self.get_object()

        league.join(request, request.user.profile)

        # If the league is "Steve's League", redirect to the league detail page + ?tour=joined
        if league.name == "Steve's League":
            url = league.get_absolute_url() + '?tour=joined'
            return redirect(url)
        return redirect('leagues:detail', pk=league.pk)


class LeaveLeagueView(LoginRequiredMixin, UpdateView):
    """
    A user can leave a league.

    Attributes:
        model (League): The thing being displayed.
        fields (list): The fields to be displayed.

    Methods:
        get(self, request, *args, **kwargs): Redirect to league detail page.
        post(self, request, *args, **kwargs): Leave the league.
    """
    model = League
    fields = []

    def get(self, request, *args, **kwargs):
        """
        Redirect to league detail page.

        Returns:
            redirect: Redirect to league detail page.
        """
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        """
        Leave the league.

        Returns:
            redirect: Redirect to league detail page.
        """
        league = self.get_object()

        if league.name == "Steve's League":
            messages.error(request, "You cannot leave Steve's League")
            return redirect('leagues:detail', pk=league.pk)
        league.leave(request, request.user.profile)
        return redirect('leagues:list')


class CreateLeagueView(LoginRequiredMixin, CreateView):
    """
    Create a new league.

    Attributes:
        model (League): The thing being displayed.
        form_class (CreateLeagueForm): The form used.

    Methods:
        form_valid(self, form): Create the league and set current user as admin.
    """
    model = League
    form_class = CreateLeagueForm

    def form_valid(self, form):
        """
        Create the league and set current user as admin.

        Args:
            form (CreateLeagueForm): The form used.

        Returns:
            redirect: Redirect to league detail page.
        """
        league = form.save()
        member = LeagueMember.objects.create(league=league, profile=self.request.user.profile, role='admin',
                                             status='joined')
        member.save()
        messages.success(self.request, f'You have created {league.name}')
        return redirect('leagues:detail', pk=league.pk)


# Admin views

class EditLeagueView(LoginRequiredMixin, UpdateView):
    """
    If the user is an admin, they can update the league.

    Attributes:
        model (League): The thing being displayed.
        form_class (EditLeagueForm): The form being used.
        template_name (str): The html template this view uses.

    Methods:
        dispatch(self, request, *args, **kwargs): Check if the user is an admin of the league.
        form_valid(self, form): Update the league.
    """
    model = League
    form_class = EditLeagueForm
    template_name = 'leagues/league_edit.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user is an admin of the league.
        If not, redirect to the league detail page.

        Returns:
            redirect: Redirect to the league detail page.
        """
        obj = self.get_object()
        # Check if the user is an admin of the league
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Update the league.

        Returns:
            redirect: Redirects to the league detail page.
        """
        league = form.save()
        messages.success(self.request, f'You have updated {league.name}')
        return redirect('leagues:detail', pk=league.pk)


class DeleteLeagueView(LoginRequiredMixin, DeleteView):
    """
    If the user is an admin, they can delete the league.

    Attributes:
        model (League): The thing being displayed.
        success_url: Redirects

    Methods:
        dispatch(self, request, *args, **kwargs): Deletes league if the user is an admin.
    """
    model = League
    success_url = reverse_lazy('leagues:list')

    def dispatch(self, request, *args, **kwargs):
        """
        Deletes league if the user is an admin.
        """
        obj = self.get_object()
        # Check if the user is an admin of the league
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)


class InviteMemberView(LoginRequiredMixin, UpdateView):
    """
    If the user is an admin, they can invite a user to the league.

    Attributes:
        model (League): The thing being displayed.
        template_name (str): The html template this view uses.
        form_class (InviteMemberForm): The form being used.

    Methods:
        dispatch(self, request, *args, **kwargs): Checks if user is admin of the league
        get_context_data(self, **kwargs): Returns list of invited members.
        get_success_url(self): Gets url of the league.
        form_valid(self, form): If the user had requested to join the league, add them to the league.
    """
    template_name = 'leagues/league_invite.html'
    model = League
    form_class = InviteMemberForm

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if user is admin of the league

        Returns:
            redirect: Redirect to the league detail page.
        """
        obj = self.get_object()
        # Check if the user is an admin of the league
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Returns list of invited members.

        Returns:
            context (dict[str, leaguemember_set]): Invited members.
        """
        context = super().get_context_data(**kwargs)
        context['invited_members'] = self.object.get_invited_members()
        return context

    def get_success_url(self):
        """
        Gets url of the league.

        Returns:
            reverse_lazy: Redirect to leagues:invite
        """
        return reverse_lazy('leagues:invite', kwargs={'pk': self.get_object().pk})

    def form_valid(self, form):
        """
        If the user had requested to join the league, add them to the league.

        Args:
            form (InviteMemberForm): The form used.

        Returns:
            redirect: Redirect to leagues:pending or leagues:invite
        """
        profile = Profile.objects.get(user__username=form.cleaned_data['username'])
        # If the user had requested to join the league, add them to the league
        league = self.get_object()
        try:
            message = league.invite(self.request, profile)
            if message == 'joined':
                return redirect('leagues:pending', pk=league.pk)
        except Exception as e:
            messages.error(self.request, e)
        return redirect('leagues:invite', pk=league.pk)


class RemoveMemberView(LoginRequiredMixin, UpdateView):
    """
    If the user is an admin, they can remove a user from the league.

    Attributes:
        model (League): The thing being displayed.

    Methods:
        dispatch(self, request, *args, **kwargs): Checks if user is admin of the league
        get(self, request, *args, **kwargs): Redirect to leagues detail page.
        post(self, request, *args, **kwargs): Remove member from a league.
    """
    model = League

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if user is admin of the league

        Returns:
            redirect: Redirect to the league detail page if user is not an admin.
        """
        obj = self.get_object()
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Redirect to leagues detail page.

        Returns:
            redirect: Redirect to leagues detail page.
        """
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        """
        Remove member from a league.

        Returns:
            redirect: Redirect to league detail page.
        """
        league = self.get_object()
        profile = Profile.objects.get(user__username=kwargs['username'])
        try:
            league.kick(request, profile)
            return redirect('leagues:detail', pk=league.pk)
        except Exception as e:
            messages.error(request, e)
            return redirect('leagues:detail', pk=league.pk)


class PendingMembersView(LoginRequiredMixin, DetailView):
    """
    If the user is an admin, they can view the members who have requested to join the league.

    Attributes:
        model (League): The thing being displayed.
        template_name (str): The html template this view uses.

    Methods:
        dispatch(self, request, *args, **kwargs): Redirect to league detail page if not an admin
            or if there are no pending members.
        get_context_data(self, **kwargs):
    """
    model = League
    template_name = 'leagues/league_pending.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect to league detail page if not an admin or if there are no pending members.

        Returns:
            redirect: Return to leagues:detail.
        """
        obj = self.get_object()
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        # If there are no pending members, redirect to the league detail page
        if not obj.get_pending_members():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Return pending members.

        Returns:
            context (dict[str, leaguemember_set]): Pending members.
        """
        context = super().get_context_data(**kwargs)
        context['pending_members'] = self.object.get_pending_members()
        return context


class PromoteMemberView(LoginRequiredMixin, UpdateView):
    """
    If the user is an admin, they can promote a member to admin.

    Attributes:
        model (League): The thing being displayed.

    Methods:
        dispatch(self, request, *args, **kwargs): Checks if user is admin of the league.
        get(self, request, *args, **kwargs): Redirect to league detail page.
        post(self, request, *args, **kwargs): Promote the user.
    """
    model = League

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if user is admin of the league.
        """
        obj = self.get_object()
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Redirect to league detail page.

        Returns:
            redirect: Redirect to leagues:detail.
        """
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        """
        Promote the user.

        Returns:
            redirect: Redirect to leagues detail page.
        """
        league = self.get_object()
        profile = Profile.objects.get(user__username=kwargs['username'])
        try:
            league.promote(self.request, profile)
        except Exception as e:
            messages.error(request, e)
        return redirect('leagues:detail', pk=league.pk)


class DemoteMemberView(LoginRequiredMixin, UpdateView):
    """
    If the user is an admin, they can demote a member from admin.

    Attributes:
        model (League): The thing being displayed.

    Methods:
        dispatch(self, request, *args, **kwargs): Checks if user is admin of the league.
        get(self, request, *args, **kwargs): Redirect to league detail page.
        post(self, request, *args, **kwargs): Demote league member.
    """
    model = League

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if user is admin of the league and return to league detail page if not.
        """
        obj = self.get_object()
        if not LeagueMember.objects.filter(league=obj, profile=request.user.profile, role='admin').exists():
            return redirect('leagues:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Redirect to league detail page.

        Returns:
            redirect: Redirect to league detail page.
        """
        return redirect('leagues:detail', pk=self.get_object().pk)

    def post(self, request, *args, **kwargs):
        """
        Demote league member.

        Returns:
            redirect: Redirect to league detail page.
        """
        league = self.get_object()
        profile = Profile.objects.get(user__username=kwargs['username'])
        try:
            league.demote(self.request, profile)
        except Exception as e:
            messages.error(request, e)
        return redirect('leagues:detail', pk=league.pk)

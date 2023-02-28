from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, DeleteView, UpdateView

from accounts.models import User
from friends.forms import UpdateProfileForm
from friends.models import FriendRequest, Profile


class ProfileView(LoginRequiredMixin, DetailView):
    """
    View to display the current user's profile
    """
    model = Profile
    template_name = 'friends/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """
        Returns the current user
        """
        if queryset is None:
            queryset = self.get_queryset()

        # Get the profile of the current user or create one if it doesn't exist
        obj, created = Profile.objects.get_or_create(user=self.request.user)
        return obj


class FriendsListView(LoginRequiredMixin, ListView):
    """
    View to display the current user's friends list as well as friend requests
    """
    template_name = 'friends/friends_list.html'
    context_object_name = 'friends'

    def __init__(self):
        super().__init__()
        self.outgoing_requests = None
        self.incoming_requests = None

    def get_queryset(self):
        """
        Returns the current user's friends and friend requests
        """
        profile = Profile.objects.get_or_create(user=self.request.user)

        # List of user's friends where the request is accepted
        friends = self.request.user.profile.get_friends()

        # Friend requests
        self.incoming_requests = FriendRequest.objects.filter(Q(to_profile=self.request.user.profile) & Q(status='p'))
        self.outgoing_requests = FriendRequest.objects.filter(Q(from_profile=self.request.user.profile) & Q(status='p'))

        return friends

    def get_context_data(self, **kwargs):
        """
        Adds friend requests to context
        """
        context = super().get_context_data(**kwargs)

        # Excluding friends and requested friends from the users queryset
        friends = self.get_queryset()
        friends_ids = [friend.id for friend in friends]
        requested_friends_ids = [friend.from_profile.user.id for friend in self.incoming_requests]
        requested_friends_ids += [friend.to_profile.user.id for friend in self.outgoing_requests]
        users = User.objects.exclude(id__in=friends_ids + requested_friends_ids + [self.request.user.id])

        context['users'] = users
        context['incoming_requests'] = self.incoming_requests
        context['outgoing_requests'] = self.outgoing_requests
        return context


class RemoveFriendView(LoginRequiredMixin, DeleteView):
    """
    View confirming the removal of a friend
    """
    model = FriendRequest
    template_name = 'friends/remove_confirmation.html'
    context_object_name = 'friend_request'
    success_url = reverse_lazy('friends:list')

    def get_object(self, queryset=None):
        """
        Returns the friend request object
        """
        friend_request = FriendRequest.objects.filter(
            Q(from_profile=self.request.user.profile) | Q(to_profile=self.request.user.profile))
        return friend_request

    def get_context_data(self, **kwargs):
        """
        Adds the friend to the context
        """
        context = super().get_context_data(**kwargs)
        context['friend'] = self.kwargs['username']
        return context

    def form_valid(self, form):
        messages.success(self.request, f'You are no longer friends with {self.kwargs["username"]}.')
        return super().form_valid(form)


class CancelFriendRequestView(LoginRequiredMixin, DeleteView):
    """
    Cancels a friend request
    """
    model = FriendRequest
    success_url = reverse_lazy('friends:list')
    context_object_name = 'friend_request'

    def get_object(self, queryset=None):
        friend_request = get_object_or_404(FriendRequest, id=self.kwargs['friend_request_id'])
        if friend_request.from_profile == self.request.user.profile:
            return friend_request
        else:
            messages.error(self.request, 'You do not have permission to cancel this friend request.')
            return None


class AddFriendView(LoginRequiredMixin, View):
    """
    View to add a friend
    Adding friends works by creating a new friend request object which is then displayed
    on the outgoing and incoming friends pages
    """

    def post(self, request, *args, **kwargs):
        """
        Adds a friend
        """
        # Get the profile of the user to be added
        profile = get_object_or_404(Profile, user__username=request.POST['username'])

        # Check if the user is already a friend
        if profile in request.user.profile.friends.all():
            messages.error(request, 'You are already friends with this user.')
            return redirect('friends:list')

        # Check if a friend request has already been sent
        if FriendRequest.objects.filter(from_profile=request.user.profile, to_profile=profile).exists():
            messages.error(request, 'You have already sent a friend request to this user.')
            return redirect('friends:list')

        # Check if a friend request has already been received
        if FriendRequest.objects.filter(from_profile=profile, to_profile=request.user.profile).exists():
            # Get the friend request
            friend_request = FriendRequest.objects.get(from_profile=profile, to_profile=request.user.profile)
            # Accept the friend request
            friend_request.accept()
            messages.success(request, f'You are now friends with {profile.user.username}!')
            return redirect('friends:list')

        # Create a new friend request
        FriendRequest.objects.create(from_profile=request.user.profile, to_profile=profile)
        messages.success(request, f'Friend request sent to {profile.user.username}!')
        return redirect('friends:list')


class AcceptFriendRequestView(LoginRequiredMixin, View):
    """
    View to accept a friend request
    Accepting the friend request works by taking the data in the FriendRequest object
    and then creating a new friends object
    """

    def post(self, request, request_id):
        # Get the friend request
        friend_request = get_object_or_404(FriendRequest, id=request_id)

        # Check if the request is addressed to the current user
        if friend_request.to_profile != request.user.profile:
            raise Http404

        # Accept the friend request
        friend_request.accept()

        messages.success(request, f'You are now friends with {friend_request.from_profile.user.username}!')

        return redirect('friends:list')


class DeclineFriendRequestView(LoginRequiredMixin, DeleteView):
    """
    Decline a friend request
    """
    model = FriendRequest
    success_url = reverse_lazy('friends:list')

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.to_profile != self.request.user.profile:
            raise Http404()
        return obj

    def form_valid(self, form):
        messages.success(self.request, 'Friend request declined.')
        return super().form_valid(form)


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """
    View to update a user's profile
    """
    model = Profile
    form_class = UpdateProfileForm
    success_url = reverse_lazy('friends:profile')
    template_name = 'friends/update_profile.html'

    def get_object(self, queryset=None):
        """
        Returns the profile of the current user
        """
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated!')
        return super().form_valid(form)

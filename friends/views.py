from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView, DeleteView

from accounts.models import User
from friends.models import FriendRequest, Friend


class ProfileView(LoginRequiredMixin, DetailView):
    """
    View to display the current user's profile
    """
    model = User
    template_name = 'friends/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        """
        Returns the current user
        """
        if queryset is None:
            queryset = self.get_queryset()

        obj = queryset.get(pk=self.request.user.pk)
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

        # List of user's friends
        friends = [friend.friend for friend in self.request.user.friends.all()]

        # Friend requests
        self.incoming_requests = FriendRequest.objects.filter(to_user=self.request.user)
        self.outgoing_requests = FriendRequest.objects.filter(from_user=self.request.user)

        return friends

    def get_context_data(self, **kwargs):
        """
        Adds friend requests to context
        """
        context = super().get_context_data(**kwargs)

        # Excluding friends and requested friends from the users queryset
        friends = self.get_queryset()
        friends_ids = [friend.id for friend in friends]
        requested_friends_ids = [friend.from_user.id for friend in self.incoming_requests]
        requested_friends_ids += [friend.to_user.id for friend in self.outgoing_requests]
        users = User.objects.exclude(id__in=friends_ids + requested_friends_ids + [self.request.user.id])

        context['users'] = users
        context['incoming_requests'] = self.incoming_requests
        context['outgoing_requests'] = self.outgoing_requests
        return context


class RemoveFriendView(LoginRequiredMixin, DetailView):
    """
    View confirming the removal of a friend
    """
    model = Friend
    template_name = 'friends/remove_confirmation.html'

    def get_object(self, queryset=None):
        """
        Returns the friend object to be removed
        """
        if queryset is None:
            queryset = self.get_queryset()

        obj = queryset.get(user__username=self.kwargs['username'], friend=self.request.user)
        return obj

    def post(self, request, *args, **kwargs):
        """
        Removes the friend
        """
        friend = get_object_or_404(Friend, friend__username=self.kwargs['username'], user=self.request.user)
        friend2 = get_object_or_404(Friend, user__username=self.kwargs['username'], friend=request.user)
        friend.delete()
        friend2.delete()
        return redirect('friends:list')


class CancelFriendRequestView(LoginRequiredMixin, DeleteView):
    """
    Cancels a friend request
    """
    model = FriendRequest
    success_url = reverse_lazy('friends:list')
    context_object_name = 'friend_request'

    def get_object(self, queryset=None):
        friend_request = get_object_or_404(FriendRequest, id=self.kwargs['friend_request_id'])
        if friend_request.from_user == self.request.user:
            return friend_request
        else:
            messages.error(self.request, 'You do not have permission to cancel this friend request.')
            return None


# adding friends works by creating a new friend request object which is then displayed
# on the outgoing and incoming friends pages


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
        username = request.POST['username']
        friend = get_object_or_404(User, username=username)

        if not request.user.friends.filter(friend=friend).exists():
            FriendRequest.objects.create(from_user=request.user, to_user=friend)
            messages.success(request, f"Friend request sent to {friend.username}")
        else:
            messages.error(request, f"{friend.username} is already your friend.")

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

        # Check if the request is addressed to the logged in user
        if friend_request.to_user != request.user:
            raise Http404

        # Add the sender to the user's friends list
        Friend.objects.create(user=request.user, friend=friend_request.from_user)
        Friend.objects.create(user=friend_request.from_user, friend=request.user)

        # Delete the friend request
        friend_request.delete()

        return redirect('friends:list')


class DeclineFriendRequestView(LoginRequiredMixin, DeleteView):
    """
    Decline a friend request
    """
    model = FriendRequest
    success_url = reverse_lazy('friends:list')

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.to_user != self.request.user:
            raise Http404()
        return obj

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Friend request declined.')
        return super().delete(request, *args, **kwargs)

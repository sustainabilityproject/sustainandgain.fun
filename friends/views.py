from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import DetailView, ListView, DeleteView, UpdateView
import operator
from functools import reduce

from accounts.models import User
from friends.forms import UpdateProfileForm
from friends.models import FriendRequest, Profile
from leagues.models import League
from tasks.models import TaskInstance


class ProfileView(LoginRequiredMixin, DetailView):
    """
    View to display the current user's profile, login required.

    Attributes:
        model (Profile): The thing being displayed.
        template_name (str): The html template this view uses.
        context_object_name (str): What this is called in the template.

    Methods:
        get_context_data(self, **kwargs): Get own profile, friends, leagues, and points.
    """
    model = Profile
    template_name = 'friends/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        """
        Get profile, friends, leagues, and points, and mutual friends if profile is not the logged in user

        Returns:
           context (dict[str, Any]): profile, friends, mutual_friends, leagues, points.
        """
        context = super().get_context_data(**kwargs)
        # defines profile depending on the existence of user_id and its value relative to the current logged in user
    
        # user id of requested profile
        user_id = self.kwargs['pk']

        if user_id != self.request.user.id:
            # if the user id is different from the current logged in user
            profile = Profile.objects.filter(id=user_id).first()
            context['other_user'] = True
        else:
            context['other_user'] = False
            profile = self.request.user.profile

        # Gets friends of profile
        friends = profile.get_friends()

        # finds mutual friends if other_user
        if context['other_user']:
            non_mutual_friends = []
            mutual_friends = []
            users_friends = self.request.user.profile.get_friends()
            for friend in friends:
                if friend in users_friends:
                    # if the friend is mutual
                    mutual_friends.append(friend)
                else:
                    non_mutual_friends.append(friend)
            
            context['friends'] = non_mutual_friends
            context['mutual_friends'] = mutual_friends
        else:
            context['friends'] = friends

        context['profile'] = profile
        context['leagues'] = League.objects.filter(leaguemember__profile=profile, leaguemember__status='joined')

        # Calculates the total points of the user
        points = 0
        for task in TaskInstance.objects.filter(profile=profile, status=TaskInstance.COMPLETED):
            points += task.task.points

        # Subtract exploded tasks
        for task in TaskInstance.objects.filter(profile=profile, status=TaskInstance.EXPLODED):
            points -= task.task.points
        
        context['points'] = points

        return context


class FriendsListView(LoginRequiredMixin, ListView):
    """
    View to display the current user's friends list as well as friend requests.

    Attributes:
        template_name (str): The html template this view uses.
        context_object_name (str): What this is called in the template.

    Methods:
        get_queryset(self): Return the current user's friends and friend requests.
        get_context_data(self, **kwargs): Add friend requests to context.

    """
    model=Profile
    template_name = 'friends/friends_list.html'
    context_object_name = 'friends'

    def __init__(self):
        super().__init__()
        self.outgoing_requests = None
        self.incoming_requests = None

    def get_queryset(self):
        """
        Return the current user's friends and friend requests.

        Returns:
            friends (list): List of user's friends.
        """
        # List of user's friends where the request is accepted
        friends = self.request.user.profile.get_friends()

        # Friend requests
        self.incoming_requests = FriendRequest.objects.filter(Q(to_profile=self.request.user.profile) & Q(status='p'))
        self.outgoing_requests = FriendRequest.objects.filter(Q(from_profile=self.request.user.profile) & Q(status='p'))

        return friends

    def get_context_data(self, **kwargs):
        """
        Add friend requests to context.

        Returns:
            context (dict[str, Any]): users, incoming requests, outgoing requests.
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
    View confirming the removal of a friend.

    Attributes:
        model (FriendRequest): The thing being displayed.
        template_name (str): The html template this view uses.
        context_object_name (str): What this is called in the template.
        success_url: Redirects.

    Methods:
        get_object(self, queryset): Returns the friend request object.
        get_context_data(self, **kwargs): Adds the friend to the context.
        form_valid(self, form): Confirm friend removal.
    """
    model = FriendRequest
    template_name = 'friends/remove_confirmation.html'
    context_object_name = 'friend_request'
    success_url = reverse_lazy('friends:list')

    def get_object(self, queryset=None):
        """
        Returns the friend request object.

        Returns:
            friend_request (FriendRequest): A friend request.
        """
        friend_request = FriendRequest.objects.filter(
            Q(from_profile=self.request.user.profile) | Q(to_profile=self.request.user.profile))
        return friend_request

    def get_context_data(self, **kwargs):
        """
        Adds the friend to the context.

        Returns:
            context (dict[str, Any]): maps friend to username.
        """
        context = super().get_context_data(**kwargs)
        context['friend'] = self.kwargs['username']
        return context

    def form_valid(self, form):
        """
        Confirm friend removal.
        """
        messages.success(self.request, f'You are no longer friends with {self.kwargs["username"]}.')
        return super().form_valid(form)


class CancelFriendRequestView(LoginRequiredMixin, DeleteView):
    """
    Cancels a friend request.

    Attributes:
        model (FriendRequest): The thing being displayed.
        success_url: Redirects.
        context_object_name (str): What this is called in the template.

    Methods:
        get_object(self, queryset): Gets request to be cancelled if the user is its sender.
    """
    model = FriendRequest
    success_url = reverse_lazy('friends:list')
    context_object_name = 'friend_request'

    def get_object(self, queryset=None):
        """
        Gets request to be cancelled if the user is its sender.

        Returns:
            friend_request (FriendRequest): The request being cancelled.
        """
        friend_request = get_object_or_404(FriendRequest, id=self.kwargs['friend_request_id'])
        if friend_request.from_profile == self.request.user.profile:
            return friend_request
        else:
            messages.error(self.request, 'You do not have permission to cancel this friend request.')
            return None


class AddFriendView(LoginRequiredMixin, View):
    """
    View to add a friend.
    Adding friends works by creating a new friend request object which is then displayed
    on the outgoing and incoming friends pages.

    Methods:
        post(self, request, *args, **kwargs): Add a friend.
    """

    def post(self, request, *args, **kwargs):
        """
        Add a friend.

        TODO the redirects
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
            return redirect(request.META['HTTP_REFERER'])

        # Create a new friend request
        FriendRequest.objects.create(from_profile=request.user.profile, to_profile=profile)
        messages.success(request, f'Friend request sent to {profile.user.username}!')

        return redirect(request.META['HTTP_REFERER'])


class AcceptFriendRequestView(LoginRequiredMixin, View):
    """
    View to accept a friend request.
    Accepting the friend request works by taking the data in the FriendRequest object
    and then creating a new friends object.

    Methods:
        post(self, request, request_id): Accept the friend request.
    """
    def post(self, request, request_id):
        """
        Accept the friend request.

        Args:
            request_id (int): The ID used to find the request.

        Returns:
            redirect: Redirect to friends list.
        """
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
    Decline a friend request.

    Attributes:
        model (FriendRequest): The thing being displayed.
        success_url: Redirects.

    Methods:
        get_object(self, queryset): Get friend request.
        form_valid(self, form): Decline the friend request.
    """
    model = FriendRequest
    success_url = reverse_lazy('friends:list')

    def get_object(self, queryset=None):
        """
        Get friend request.
        Raise 404 if the recipient is not the current profile.

        Returns:
            obj (FriendRequest): The friend request.
        """
        obj = super().get_object()
        if obj.to_profile != self.request.user.profile:
            raise Http404()
        return obj

    def form_valid(self, form):
        """
        Decline the friend request.
        """
        messages.success(self.request, 'Friend request declined.')
        return super().form_valid(form)


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """
    View to update a user's profile.

    Attributes:
        model (Profile): The thing being displayed.
        form_class (UpdateProfileForm): The form used.
        template_name (str): The html template this view uses.

    Methods:
        get_success_url(self): TODO
        get_object(self, queryset): Return the profile of the current user.
        form_valid(self, form): Update profile.
    """
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'friends/update_profile.html'

    def get_success_url(self):
        """
        TODO
        """
        return reverse('friends:profile', kwargs={'pk': self.request.user.profile.id})

    def get_object(self, queryset=None):
        """
        Returns the profile of the current user

        Returns:
            Profile: The current user's profile.
        """
        return self.request.user.profile

    def form_valid(self, form):
        """
        Update profile.
        """
        messages.success(self.request, 'Profile updated!')
        return super().form_valid(form)


class ProfileSearchView(ListView):
    """
    View to provide a basic search for users.

    Attributes:
        model (User): The thing being displayed.
        template_name (str): The html template this view uses.

    Methods:
        get_queryset(self): Return users whose names or usernames match the query.
        get_context_data(self, **kwargs): Determines if the search came from the friends page.
    """
    model = User
    template_name = 'friends/profile_search.html'

    def get_queryset(self):
        """
        Return users whose names or usernames match the query.
        If the query is made from the friends page, current friends will not be included.

        Returns:
            objects_list (list[User]): List of filtered and ordered users.
        """

        # url parameter q
        query = self.request.GET.get("q").strip()
        # list of words in q all set to lowercase
        query_tokens = [q.lower() for q in query.split()]

        # f only exists if the search is made from the friends page
        f = self.request.GET.get("f")

        # list of id of users to remove from final list
        exclusions = [self.request.user.id]

        if f:
            # adds friends and potential friends to exclusion list
            friend_ids = [
                friend.id for friend in self.request.user.profile.get_friends(status='all')
                ]
            exclusions.extend(friend_ids)

        if len(query_tokens) == 0:
            # if there are no tokens then there are no search results
            return None
        if len(query_tokens) == 1:

            # contains three list, for basic ranking of search output
            temp_obj_list = [[], [], []]

            object_list = User.objects.filter(
                Q(username__istartswith=query) |
                Q(first_name__istartswith=query) |
                Q(last_name__istartswith=query)
            ).exclude(id__in=exclusions)

            # bins users into 3 ranks
            for user in object_list:
                # since one word was searched for, it is assumed that the username is being searched for
                # therefore the query bing in username is weighted more than the query being in the first of last name
                count = 0
                # if query is in username increase count by 2
                count += 2*len(object_list.filter(Q(id = user.id) & Q(username__istartswith=query)))
                # count increases by 1 if query is in first_name or last name, else 0
                count += len(object_list.filter(Q(id = user.id) & Q(Q(first_name__istartswith=query) | Q(last_name__istartswith=query))))

                # query is just in first or last name
                if count == 1:
                    temp_obj_list[2].append(user)
                # query is just in the username
                elif count == 2:
                    temp_obj_list[1].append(user)
                # query is in other username and first or last name
                elif count == 3:
                    temp_obj_list[0].append(user)

        else:
            # contains three list, for basic ranking of search output
            temp_obj_list = [[], [], [], [], []]

            object_list = User.objects.filter(
                # is username in any of the values
                reduce(operator.or_, (Q(username__istartswith=q) for q in query_tokens)) |
                # it is assumed that the last value in query is not a first name
                reduce(operator.or_, (Q(first_name__istartswith=q) for q in query_tokens[0:-1] )) |
                # it is assumed that the first value in query is not a last name
                reduce(operator.or_, (Q(last_name__istartswith=q) for q in query_tokens[1:] ))
            ).exclude(id__in=exclusions)

            # bins users into 5 basic ranks
            for user in object_list:
                # here multiple words were in the search query,
                # therefore it is assumed that a name is being searched for,
                # therefore query being in the first or last name is weighted more than it being in the username

                count = 0
                # if query is in username increase count by 1
                for t in query_tokens:
                    if user.username.lower().find(t) == 0:
                        count += 1
                        break
                # if query is in first name increase count 2
                if user.first_name != '':
                    for t in query_tokens[0:-1]:
                        if user.first_name.lower()[0:len(t)] == t:
                            count += 2
                            break
                # if query is in first name increase count 2
                if user.last_name != '':
                    for t in query_tokens[1:]:
                        if user.last_name.lower()[0:len(t)] == t:
                            count += 2
                            break

                # query is just in username
                if count == 1:
                    temp_obj_list[4].append(user)
                # query is in just first or last name
                elif count == 2:
                    temp_obj_list[3].append(user)
                # query is in first or last name and the username
                elif count == 3:
                    temp_obj_list[2].append(user)
                # query is in first and last name
                elif count == 4:
                    temp_obj_list[1].append(user)
                # query is in username and first name and last name
                elif count == 5:
                    temp_obj_list[0].append(user)

        # flattens temp_obj_list
        object_list = [user for list in temp_obj_list for user in list]

        # sets object_list to None so that the template knows there were no search results
        if len(object_list) == 0:
            object_list = None

        return object_list

    def get_context_data(self, **kwargs):
        """
        Determines if the search came from the friends page.

        Returns:
            context (dict[str, Any]): Context data for the template.
        """

        context = super().get_context_data(**kwargs)
        # only exists of the search was made from the search page
        f = self.request.GET.get("f")

        if f is not None:
            # lets the template know that the user has made the search from the friends page
            context['searching_for_friend'] = True

        return context


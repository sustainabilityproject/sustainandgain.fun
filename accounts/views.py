from accounts.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Friend, FriendRequest


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"

def profile(request):
    return render(request, 'account/profile.html')

# render the friends list page with the incoming and outgoing friend requests
@login_required
def friends_list(request):
    # list of friends as user objects
    friends = [friend.friend for friend in request.user.friends.all()]
    # list of users
    users = User.objects.exclude(id=request.user.id)

    incoming_requests = FriendRequest.objects.filter(to_user=request.user)
    outgoing_requests = FriendRequest.objects.filter(from_user=request.user)
    return render(request, 'account/friends_list.html', {'friends': friends,
                                                         'users': users,
                                                         'incoming_requests': incoming_requests,
                                                         'outgoing_requests': outgoing_requests,
                                                         })

# remove friend from both users friends lists
@login_required
def remove_friend(request, username):
    friend = get_object_or_404(Friend, friend__username=username, user=request.user)
    friend2 = get_object_or_404(Friend, user__username=username, friend=request.user)
    friend.delete()
    friend2.delete()
    return redirect('friends_list')

# cancel the friend request removes from both users pages
@login_required
def cancel_friend_request(request, friend_request_id):
    friend_request = get_object_or_404(FriendRequest, id=friend_request_id)

    if friend_request.from_user == request.user:
        friend_request.delete()
        messages.success(request, 'Friend request canceled.')
    else:
        messages.error(request, 'You do not have permission to cancel this friend request.')

    return redirect('friends_list')

# adding friends works by creating a new friend request object which is then displayed 
# on the outgoing and incoming friends pages
@login_required
def add_friend(request):
    if request.method == 'POST':
        username = request.POST['username']
        friend = get_object_or_404(User, username=username)

        if not request.user.friends.filter(friend=friend).exists():
            FriendRequest.objects.create(from_user=request.user, to_user=friend)
            messages.success(request, f"Friend request sent to {friend.username}")
        else:
            messages.error(request, f"{friend.username} is already your friend.")

    return HttpResponseRedirect(reverse('friends_list'))


# accepting the friend request works by taking the data in the friendrequest object and then creating a new friends object
@login_required
def accept_friend_request(request, request_id):
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
    
    return redirect('friends_list')

# this method works by just deleting the friendrequest object
@login_required
def decline_friend_request(request, request_id):
    # Get the friend request
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    
    # Check if the request is addressed to the logged in user
    if friend_request.to_user != request.user:
        raise Http404
    
    # Delete the friend request
    friend_request.delete()
    
    return redirect('friends_list')

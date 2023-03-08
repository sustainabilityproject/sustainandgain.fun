from django import forms

from accounts.models import User
from leagues.models import LeagueMember, League


class CreateLeagueForm(forms.ModelForm):
    """
    Form used by a user to create a new league.
    """

    class Meta:
        model = League
        fields = ['name', 'description', 'visibility', 'invite_only']

    def clean_name(self):
        name = self.cleaned_data['name']
        if League.objects.filter(name=name).exists():
            raise forms.ValidationError('A league with that name already exists')
        return name

    def clean(self):
        """
        If the league is private, it must be invite-only.
        """
        cleaned_data = super().clean()
        visibility = cleaned_data.get('visibility')
        invite_only = cleaned_data.get('invite_only')
        if visibility == 'private' and not invite_only:
            raise forms.ValidationError('Private leagues must be invite only')
        return cleaned_data


class EditLeagueForm(forms.ModelForm):
    """
    Form used by a league admin to update the league details.
    """

    class Meta:
        model = League
        fields = ['name', 'description', 'visibility', 'invite_only']

    def clean_name(self):
        name = self.cleaned_data['name']
        if League.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A league with that name already exists')
        return name

    def clean(self):
        """
        If the league is private, it must be invite-only.
        """
        cleaned_data = super().clean()
        visibility = cleaned_data.get('visibility')
        invite_only = cleaned_data.get('invite_only')
        if visibility == 'private' and not invite_only:
            raise forms.ValidationError('Private leagues must be invite only')
        return cleaned_data


class InviteMemberForm(forms.ModelForm):
    """
    Form used by an admin of a league to invite a user to join the league.
    """
    username = forms.CharField(max_length=100)

    class Meta:
        model = League
        fields = ['username']

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('User does not exist')
        return username

    def clean(self):
        """
        Check if the user is already a member of the league or has already been invited.
        """
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        if username:
            if LeagueMember.objects.filter(league=self.instance, profile__user__username=username,
                                           status='joined').exists():
                raise forms.ValidationError(f'{username} is already a member of {self.instance.name}')
            if LeagueMember.objects.filter(league=self.instance, status='invited',
                                           profile__user__username=username).exists():
                raise forms.ValidationError(f'{username} has already been invited to {self.instance.name}')
        return cleaned_data

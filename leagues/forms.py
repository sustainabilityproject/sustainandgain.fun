from django import forms

from accounts.models import User
from leagues.models import LeagueMember, League


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

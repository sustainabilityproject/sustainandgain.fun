from django.contrib import admin

from friends.models import Profile, FriendRequest


class FriendsInline(admin.TabularInline):
    model = FriendRequest
    extra = 0
    fk_name = 'from_profile'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj is not None:
            user_profile = obj
            if user_profile == formset.form.base_fields['from_profile'].initial:
                formset.form.base_fields['to_profile'].queryset = Profile.objects.exclude(
                    id=user_profile.id)
                formset.fk_name = 'from_profile'
            elif user_profile == formset.form.base_fields['to_profile'].initial:
                formset.form.base_fields['from_profile'].queryset = Profile.objects.exclude(
                    id=user_profile.id)
                formset.fk_name = 'to_profile'
        return formset


class ProfileAdmin(admin.ModelAdmin):
    inlines = [FriendsInline]


admin.site.register(Profile, ProfileAdmin)

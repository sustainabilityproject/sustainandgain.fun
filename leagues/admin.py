from django.contrib import admin

from leagues.models import League


class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    filter_horizontal = ('members',)


admin.site.register(League, LeagueAdmin)
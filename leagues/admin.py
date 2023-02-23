from django.contrib import admin

from .models import League, LeagueMember


class LeagueMemberInline(admin.TabularInline):
    model = LeagueMember
    extra = 0


class LeagueAdmin(admin.ModelAdmin):
    inlines = [LeagueMemberInline]


admin.site.register(League, LeagueAdmin)

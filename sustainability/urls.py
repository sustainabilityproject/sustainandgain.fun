"""sustainability URL Configuration"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from feed.views import HomeView

admin.site.site_header = 'Gamekeeper Area'
admin.site.site_title = 'Gamekeeper Area'
admin.site.index_title = 'Gamekeeper Area'

urlpatterns = [
    # Account routes
    # path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),

    # Task routes
    path('tasks/', include('tasks.urls')),

    # Friends routes
    path('friends/', include('friends.urls')),

    # Leagues routes
    path('leagues/', include('leagues.urls')),

    # Feed
    path('feed/', include('feed.urls')),

    # Home route
    path('', HomeView.as_view(), name='home'),

    # Notifications
    path('notifications/', include('notifications.urls')),

    # Gamekeeper routes
    path('gamekeeper/', admin.site.urls),

    # Robots.txt
    path('robots.txt', RedirectView.as_view(url='/static/robots.txt', permanent=True), ),

    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True), ),

    # Policy path
    path('about/', include('about.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

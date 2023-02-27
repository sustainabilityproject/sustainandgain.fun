"""sustainability URL Configuration"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from feed.views import HomeView

urlpatterns = [
    # Admin routes
    path('admin/', admin.site.urls),

    # Account routes
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.urls import path

from about.views import PrivacyPolicyView, AboutView

app_name = 'about'
urlpatterns = [
    path('privacy', PrivacyPolicyView.as_view(), name='privacy'),
    path('', AboutView.as_view(), name='about')
]

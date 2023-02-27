
from django.urls import path

from feed.views import FeedView
from feed.views import LikeView
from feed.views import ReportView


app_name = "feed"
urlpatterns = [
    path('', FeedView.as_view(), name='feed'),
    path('like/<int:pk>/', LikeView.as_view(), name='like'),
    path('report/<int:pk>/', ReportView.as_view(), name='report')
]


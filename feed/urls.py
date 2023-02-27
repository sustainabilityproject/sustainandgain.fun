
from django.urls import path

from feed.views import FeedView
from feed.views import LikeView
from feed.views import ReportView
from feed.views import ReportedView
from feed.views import DeleteView
from feed.views import RestoreView


app_name = "feed"
urlpatterns = [
    path('', FeedView.as_view(), name='feed'),
    path('like/<int:pk>/', LikeView.as_view(), name='like'),
    path('report/<int:pk>/', ReportView.as_view(), name='report'),
    path('reported/', ReportedView.as_view(), name='reported'),
    path('delete/<int:pk>/', DeleteView.as_view(), name='delete'),
    path('restore/<int:pk>/', RestoreView.as_view(), name='restore')
]


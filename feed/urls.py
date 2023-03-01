
from django.urls import path

from feed.views import FeedView
from feed.views import LikeTaskView
from feed.views import ReportTaskView
from feed.views import ReportedTasksView
from feed.views import DeleteTaskView
from feed.views import RestoreTaskView


app_name = "feed"
urlpatterns = [
    path('', FeedView.as_view(), name='feed'),
    path('like/<int:pk>/', LikeTaskView.as_view(), name='like'),
    path('report/<int:pk>/', ReportTaskView.as_view(), name='report'),

    # Staff views
    path('reported/', ReportedTasksView.as_view(), name='reported'),
    path('delete/<int:pk>/', DeleteTaskView.as_view(), name='delete'),
    path('restore/<int:pk>/', RestoreTaskView.as_view(), name='restore')
]


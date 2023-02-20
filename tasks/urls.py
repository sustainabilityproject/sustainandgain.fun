from django.urls import path
from tasks.views import IndexView, MyTasksView

from . import views

urlpatterns = [
    path('', IndexView.as_view(), name='tasks_index'),
    path('mytasks/', MyTasksView.as_view(), name='my_tasks')
]

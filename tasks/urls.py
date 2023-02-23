from django.urls import path

from tasks.views import IndexView, MyTasksView, accept_task, CompleteTaskView

urlpatterns = [
    path('', IndexView.as_view(), name='tasks_index'),
    path('mytasks/', MyTasksView.as_view(), name='my_tasks'),
    path('<int:task_id>/accept', accept_task, name='accept_task'),
    path('<int:pk>/complete', CompleteTaskView.as_view(), name='complete_task'),
]

from django.urls import path
from tasks.views import IndexView, MyTasksView, accept_task

from . import views


urlpatterns = [
    path('', IndexView.as_view(), name='tasks_index'),
    path('mytasks/', MyTasksView.as_view(), name='my_tasks'),
    path('<int:task_id>/accept', accept_task, name='accept_task'),
    path('take-photo/', views.TakePhotoView.as_view(), name='take_photo')
]

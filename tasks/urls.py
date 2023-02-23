from django.urls import path

from tasks.views import IndexView, MyTasksView, accept_task, CompleteTaskView, TakePhotoView

app_name = 'tasks'
urlpatterns = [
    path('', MyTasksView.as_view(), name='list'),
    path('available/', IndexView.as_view(), name='available'),
    path('<int:task_id>/accept/', accept_task, name='accept'),
    path('<int:pk>/complete/', CompleteTaskView.as_view(), name='complete'),
    path('take-photo/', TakePhotoView.as_view(), name='take_photo')
]

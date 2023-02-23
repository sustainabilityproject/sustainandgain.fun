from django.urls import path

from tasks.views import IndexView, MyTasksView, AcceptTaskView, CompleteTaskView, TakePhotoView

app_name = 'tasks'
urlpatterns = [
    path('', MyTasksView.as_view(), name='list'),
    path('available/', IndexView.as_view(), name='available'),
    path('<int:pk>/accept/', AcceptTaskView.as_view(), name='accept'),
    path('<int:pk>/complete/', CompleteTaskView.as_view(), name='complete'),
    path('take-photo/', TakePhotoView.as_view(), name='take_photo')
]

from django.urls import path
from .views import (
    TasksView,
    TaskDetailView,
    CreateTaskView,
    UpdateTaskView,
    DeleteTaskView,
    UsersView,
    UserDetailView
)

urlpatterns = [

    path('tasks/', TasksView.as_view()),
    path('tasks/<int:id>/', TaskDetailView.as_view()),
    path('tasks/create/', CreateTaskView.as_view()),
    path('tasks/update/<int:id>/',
         UpdateTaskView.as_view()),
    path('tasks/delete/<int:id>/',
         DeleteTaskView.as_view()),

    path('users/',
         UsersView.as_view()),

    path('user-search/',
         UserDetailView.as_view()),
]
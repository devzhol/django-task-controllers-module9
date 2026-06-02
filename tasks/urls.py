from django.urls import path
from .views import (
    HomeView,
    TasksPageView,
    UsersPageView,
    AboutView,
    ContactView,
    TasksView,
    TaskDetailView,
    CreateTaskView,
    UpdateTaskView,
    DeleteTaskView,
    UsersView,
    UserDetailView,
    BBCodeView,
    IceCreamCreateView,
    IceCreamBatchCreateView
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

         path(
    '',
    HomeView.as_view()
),

path(
    'tasks-page/',
    TasksPageView.as_view()
),

path(
    'users-page/',
    UsersPageView.as_view()
),

path(
    'about/',
    AboutView.as_view()
),

path(
    'contact/',
    ContactView.as_view()
),
path(
    'bbcode/',
    BBCodeView.as_view()
),
path(
    'icecream/create/',
    IceCreamCreateView.as_view()
),
path(
    'icecream/batch/',
    IceCreamBatchCreateView.as_view()
),
]

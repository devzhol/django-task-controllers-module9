from django.urls import path
from .views import *

urlpatterns = [

    # Все задачи
    path('tasks/', get_tasks),

    # Одна задача
    path('tasks/<int:id>/', get_task),

    # Создание
    path('tasks/create/', create_task),

    # Обновление
    path('tasks/update/<int:id>/', update_task),

    # Удаление
    path('tasks/delete/<int:id>/', delete_task),
]
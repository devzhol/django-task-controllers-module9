from django.http import JsonResponse
from django.views import View


# Временная база задач
tasks = [

    {
        'id': 1,
        'title': 'Изучить Django',
        'completed': False
    },

    {
        'id': 2,
        'title': 'Сделать домашнее задание',
        'completed': True
    },
]


# Получение всех задач
class TasksView(View):

    def get(self, request):

        return JsonResponse(
            tasks,
            safe=False
        )


# Получение одной задачи
class TaskDetailView(View):

    def get(self, request, id):

        for task in tasks:

            if task['id'] == id:
                return JsonResponse(task)

        return JsonResponse({
            'error': 'Задача не найдена'
        })


# Создание задачи
class CreateTaskView(View):

    def get(self, request):

        new_task = {

            'id': len(tasks) + 1,
            'title': f'Новая задача {len(tasks)+1}',
            'completed': False
        }

        tasks.append(new_task)

        return JsonResponse({
            'message': 'Задача создана',
            'task': new_task
        })


# Обновление задачи
class UpdateTaskView(View):

    def get(self, request, id):

        for task in tasks:

            if task['id'] == id:

                task['completed'] = True

                return JsonResponse({
                    'message': 'Задача обновлена',
                    'task': task
                })

        return JsonResponse({
            'error': 'Задача не найдена'
        })


# Удаление задачи
class DeleteTaskView(View):

    def get(self, request, id):

        for task in tasks:

            if task['id'] == id:

                tasks.remove(task)

                return JsonResponse({
                    'message': 'Задача удалена'
                })

        return JsonResponse({
            'error': 'Задача не найдена'
        })
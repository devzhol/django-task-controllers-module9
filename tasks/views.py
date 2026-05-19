from django.http import JsonResponse


# Временная база данных
tasks = [

    {
        'id': 1,
        'title': 'Изучить Django',
        'completed': False
    },

    {
        'id': 2,
        'title': 'Сделать домашку',
        'completed': True
    },

    {
        'id': 3,
        'title': 'Загрузить проект на GitHub',
        'completed': False
    },
]


# Получение всех задач
def get_tasks(request):

    return JsonResponse(tasks, safe=False)


# Получение одной задачи
def get_task(request, id):

    for task in tasks:

        if task['id'] == id:
            return JsonResponse(task)

    return JsonResponse({
        'error': 'Задача не найдена'
    })


# Создание задачи
def create_task(request):

    new_task = {

        'id': len(tasks) + 1,
        'title': f'Новая задача {len(tasks) + 1}',
        'completed': False
    }

    tasks.append(new_task)

    return JsonResponse({
        'message': 'Задача создана',
        'task': new_task
    })


# Обновление задачи
def update_task(request, id):

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
def delete_task(request, id):

    for task in tasks:

        if task['id'] == id:

            tasks.remove(task)

            return JsonResponse({
                'message': 'Задача удалена'
            })

    return JsonResponse({
        'error': 'Задача не найдена'
    })
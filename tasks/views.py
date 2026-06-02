from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View  
from .forms import UserSearchForm
from django.shortcuts import render

class BBCodeView(View):

    def get(self, request):

        text = """

[b]Django[/b]
[i]Web-development[/i]

[url=https://djangoproject.com]
Official site
[/url]

"""

        comma_text = 'Alihan,Dana,Django,Python'

        return render(
            request,
            'bbcode_page.html',
            {
                'text': text,
                'comma_text': comma_text
            }
        )

tasks_data = [

    {
        'title': 'Изучить Django'
    },

    {
        'title': 'Сделать ДЗ'
    }
]


users_data = [

    {
        'name': 'Alihan'
    },

    {
        'name': 'Dana'
    }
]


class HomeView(View):

    def get(self, request):

        return render(
            request,
            'home.html'
        )


class TasksPageView(View):

    def get(self, request):

        paginator = Paginator(tasks_data, 1)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            'tasks.html',
            {
                'tasks': page_obj.object_list,
                'page_obj': page_obj,
            }
        )


class UsersPageView(View):

    def get(self, request):

        return render(
            request,
            'users.html',
            {
                'users': users_data
            }
        )


class AboutView(View):

    def get(self, request):

        return render(
            request,
            'about.html'
        )


class ContactView(View):

    def get(self, request):

        return render(
            request,
            'contact.html'
        )

# Временная база пользователей
users = [

    {
        'id': 1,
        'name': 'Alihan',
        'email': 'alihan@gmail.com'
    },

    {
        'id': 2,
        'name': 'Askar',
        'email': 'askar@gmail.com'
    },

    {
        'id': 3,
        'name': 'Dana',
        'email': 'dana@gmail.com'
    },
]


# Все пользователи
class UsersView(View):

    def get(self, request):

        return JsonResponse(
            users,
            safe=False
        )


# Поиск пользователя через форму
class UserDetailView(View):

    def get(self, request):

        form = UserSearchForm()

        return render(
            request,
            'user_search.html',
            {
                'form': form
            }
        )

    def post(self, request):

        form = UserSearchForm(
            request.POST
        )

        if form.is_valid():

            user_id = form.cleaned_data[
                'user_id'
            ]

            for user in users:

                if user['id'] == user_id:

                    return JsonResponse(
                        user
                    )

            return JsonResponse({
                'error':
                'Пользователь не найден'
            })

        return render(
            request,
            'user_search.html',
            {
                'form': form
            }
        )


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
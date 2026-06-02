from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View  
from .forms import UserSearchForm, IceCreamForm, ContactForm, UserProfileForm
from .models import ContactMessage, IceCream, Recipe, Ingredient, GourmetIceCream, UserProfile


def get_user_manager_group():
    group, _ = Group.objects.get_or_create(name='UserManagers')
    user_ct = ContentType.objects.get_for_model(User)
    permissions = Permission.objects.filter(
        content_type=user_ct,
        codename__in=['add_user', 'change_user', 'delete_user', 'view_user']
    )
    group.permissions.set(permissions)
    group.user_set.add(*User.objects.filter(is_superuser=True))
    return group


def user_is_manager(user):
    return user.is_authenticated and user.groups.filter(name='UserManagers').exists()

class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            group = get_user_manager_group()
            group.user_set.add(user)

            print('AUTH INFO:')
            print('username=', user.username)
            print('is_authenticated=', user.is_authenticated)
            print('is_superuser=', user.is_superuser)
            print('groups=', [group.name for group in user.groups.all()])
            print('perms=', sorted(user.get_all_permissions()))

            return redirect('/users-page/')

        return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль.'})


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('/login/')


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


class RecipeListView(View):

    def get(self, request):
        if not Ingredient.objects.exists():
            tomatoes = Ingredient.objects.create(name='Tomato')
            basil = Ingredient.objects.create(name='Basil')
            mozzarella = Ingredient.objects.create(name='Mozzarella')
            flour = Ingredient.objects.create(name='Flour')
            olive_oil = Ingredient.objects.create(name='Olive oil')

            margherita = Recipe.objects.create(
                title='Pizza Margherita',
                description='Classic Italian pizza with tomato, mozzarella and basil.'
            )
            margherita.ingredients.set([tomatoes, basil, mozzarella, olive_oil])

            bruschetta = Recipe.objects.create(
                title='Bruschetta',
                description='Toasted bread with tomato, basil and olive oil.'
            )
            bruschetta.ingredients.set([tomatoes, basil, olive_oil, flour])

        recipes = Recipe.objects.only('title').prefetch_related(
            'ingredients'
        )

        recipe_list = []
        for recipe in recipes:
            recipe_list.append({
                'title': recipe.title,
                'ingredients': [ingredient.name for ingredient in recipe.ingredients.only('name')],
            })

        return render(request, 'recipes.html', {'recipes': recipe_list})


class GourmetIceCreamListView(View):

    def get(self, request):
        if not GourmetIceCream.objects.exists():
            GourmetIceCream.objects.create(
                name='Bella Gelato',
                price=5.50,
                description='Creamy gelato with premium vanilla.',
                dairy_free=False,
                category='Dessert',
                sweetness_level='High',
                flavor='Vanilla',
                scoop_size='Large'
            )
            GourmetIceCream.objects.create(
                name='Berry Dream',
                price=6.20,
                description='Fresh berry sorbet with bright fruit flavor.',
                dairy_free=True,
                category='Dessert',
                sweetness_level='Medium',
                flavor='Berry',
                scoop_size='Medium'
            )

        gourmet_list = GourmetIceCream.objects.only('name', 'flavor', 'price')
        return render(request, 'gourmet_icecream.html', {'gourmet_list': gourmet_list})


@method_decorator(user_passes_test(user_is_manager, login_url='/login/'), name='dispatch')
class UsersPageView(View):

    def get(self, request):

        return render(
            request,
            'users.html',
            {
                'users': users_data
            }
        )


class IceCreamCreateView(View):

    def get(self, request):
        form = IceCreamForm()
        return render(request, 'icecream_form.html', {'form': form})

    def post(self, request):
        form = IceCreamForm(request.POST)
        if form.is_valid():
            icecream = form.save()
            return render(request, 'icecream_success.html', {'icecream': icecream})

        return render(request, 'icecream_form.html', {'form': form})


class IceCreamBatchCreateView(View):

    def get(self, request):
        IceCreamFormSet = modelformset_factory(
            IceCream,
            form=IceCreamForm,
            fields=['name', 'flavor', 'price'],
            extra=3,
            validate_max=False,
        )
        formset = IceCreamFormSet(queryset=IceCream.objects.none())
        return render(request, 'icecream_batch_form.html', {'formset': formset})

    def post(self, request):
        IceCreamFormSet = modelformset_factory(
            IceCream,
            form=IceCreamForm,
            fields=['name', 'flavor', 'price'],
            extra=3,
            validate_max=False,
        )
        formset = IceCreamFormSet(request.POST, queryset=IceCream.objects.none())

        if formset.is_valid():
            icecreams = formset.save()
            return render(request, 'icecream_batch_success.html', {'icecreams': icecreams})

        return render(request, 'icecream_batch_form.html', {'formset': formset})


class AboutView(View):

    def get(self, request):

        return render(
            request,
            'about.html'
        )


class ContactView(View):

    def get(self, request):
        form = ContactForm()
        return render(request, 'contact.html', {'form': form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
            )
            return render(request, 'contact.html', {
                'form': ContactForm(),
                'success': 'Сообщение успешно сохранено.'
            })

        return render(request, 'contact.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = UserProfileForm(instance=profile)
        return render(request, 'profile_form.html', {'form': form})

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return render(request, 'profile_form.html', {
                'form': form,
                'success': 'Профиль успешно сохранён.'
            })
        return render(request, 'profile_form.html', {'form': form})

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
@method_decorator(user_passes_test(user_is_manager, login_url='/login/'), name='dispatch')
class UsersView(View):

    def get(self, request):

        return JsonResponse(
            users,
            safe=False
        )


# Поиск пользователя через форму
@method_decorator(user_passes_test(user_is_manager, login_url='/login/'), name='dispatch')
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
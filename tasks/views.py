from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from .forms import (
    UserSearchForm, IceCreamForm, ContactForm, UserProfileForm, 
    DocumentUploadForm, UserLoginForm, UserRegistrationForm,
    CustomPasswordResetForm, CustomSetPasswordForm
)
from .models import ContactMessage, IceCream, Recipe, Ingredient, GourmetIceCream, UserProfile, Document


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
    """Представление для входа пользователя"""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/users-page/')
        form = UserLoginForm()
        return render(request, 'auth/login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                
                # "Remember me" functionality
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser session
                
                # Add user to managers group
                group = get_user_manager_group()
                group.user_set.add(user)

                return redirect('/users-page/')
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль.')

        return render(request, 'auth/login.html', {'form': form})


class LogoutView(View):
    """Представление для выхода пользователя"""

    def get(self, request):
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            return render(request, 'auth/logout_success.html', {'username': username})
        return redirect('/login/')


class RegisterView(View):
    """Представление для регистрации нового пользователя"""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/users-page/')
        form = UserRegistrationForm()
        return render(request, 'auth/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data.get('first_name', ''),
                    last_name=form.cleaned_data.get('last_name', '')
                )
                # Create user profile
                UserProfile.objects.get_or_create(user=user)
                
                # Add to UserManagers group
                group = get_user_manager_group()
                group.user_set.add(user)
            
            return render(request, 'auth/register_success.html', {'username': user.username})

        return render(request, 'auth/register.html', {'form': form})


class PasswordResetView(View):
    """Представление для запроса восстановления пароля"""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/users-page/')
        form = CustomPasswordResetForm()
        return render(request, 'auth/password_reset.html', {'form': form})

    def post(self, request):
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(f'/password-reset-confirm/{uid}/{token}/')
            
            # Send email
            subject = 'Восстановление пароля - Task List'
            message = render_to_string('auth/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
                'email': email,
            })
            
            send_mail(
                subject,
                message,
                'noreply@tasklistapp.com',
                [email],
                fail_silently=False,
            )
            
            return render(request, 'auth/password_reset_done.html', {'email': email})

        return render(request, 'auth/password_reset.html', {'form': form})


class PasswordResetConfirmView(View):
    """Представление для подтверждения восстановления пароля"""

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            request.session['reset_user_id'] = user.id
            form = CustomSetPasswordForm()
            return render(request, 'auth/password_reset_confirm.html', {
                'form': form,
                'uidb64': uidb64,
                'token': token,
                'valid_link': True,
            })
        else:
            return render(request, 'auth/password_reset_confirm.html', {
                'valid_link': False,
            })

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = CustomSetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()
                
                # Clear session
                if 'reset_user_id' in request.session:
                    del request.session['reset_user_id']
                
                return render(request, 'auth/password_reset_complete.html', {'username': user.username})
            
            return render(request, 'auth/password_reset_confirm.html', {
                'form': form,
                'uidb64': uidb64,
                'token': token,
                'valid_link': True,
            })
        else:
            return render(request, 'auth/password_reset_confirm.html', {
                'valid_link': False,
            })


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


# ============ Document Upload Views ============

class DocumentUploadView(View):
    """Представление для загрузки документов"""

    @method_decorator(login_required(login_url='/login/'))
    def get(self, request):
        form = DocumentUploadForm()
        return render(request, 'document_upload.html', {'form': form})

    @method_decorator(login_required(login_url='/login/'))
    def post(self, request):
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            return redirect('document_list')
        return render(request, 'document_upload.html', {'form': form})


class DocumentListView(View):
    """Представление для просмотра списка загруженных документов"""

    @method_decorator(login_required(login_url='/login/'))
    def get(self, request):
        documents = Document.objects.all()
        paginator = Paginator(documents, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'document_list.html', {
            'documents': page_obj.object_list,
            'page_obj': page_obj,
        })
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from localflavor.generic.models import IBANField
from localflavor.us.models import USStateField, USZipCodeField


class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    ingredients = models.ManyToManyField('Ingredient', related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class IceCream(models.Model):
    name = models.CharField(max_length=100)
    flavor = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    dairy_free = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.flavor})"


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    state = USStateField(default='NY')
    postal_code = USZipCodeField()
    iban = IBANField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} from {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FoodProduct(Product):
    dairy_free = models.BooleanField(default=False)
    category = models.CharField(max_length=50, default='Food')


class Dessert(FoodProduct):
    sweetness_level = models.CharField(max_length=50, default='Medium')


class GourmetIceCream(Dessert):
    flavor = models.CharField(max_length=100)
    scoop_size = models.CharField(max_length=50, default='Standard')

    def __str__(self):
        return f"{self.name} ({self.flavor})"


class Document(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название документа')
    description = models.TextField(blank=True, verbose_name='Описание')
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'xlsx'])],
        help_text='Поддерживаются только файлы .pdf и .xlsx',
        verbose_name='Файл'
    )
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return f"{self.title} ({self.file.name})"

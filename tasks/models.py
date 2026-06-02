from django.db import models


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

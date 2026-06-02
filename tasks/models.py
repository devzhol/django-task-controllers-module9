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

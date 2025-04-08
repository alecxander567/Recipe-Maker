from django.db import models
from django.contrib.auth.models import User

class UserAccount(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('chef', 'Chef'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    profile_picture = models.ImageField(upload_to='user_pics/', null=True, blank=True)
    favorites = models.ManyToManyField('Recipe', related_name="favorite_recipes", blank=True)  # Forward ref

    def __str__(self):
        return self.user.username 


class Recipe(models.Model):
    chef = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="recipes")
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='recipes/')

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.value for r in ratings) / ratings.count(), 1)
        return None

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.user.username} - {self.recipe.name}"


class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField()

    def __str__(self):
        return f"{self.recipe.name} - {self.value}/5"

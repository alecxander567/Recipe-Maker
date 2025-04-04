from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

class ChefProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/userprof.avif')

    def __str__(self):
        return self.full_name


class UserAccount(models.Model):
    """Model for Regular Users"""
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def set_password(self, raw_password):
        """Hashes and saves the password"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Checks the hashed password"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username
    
    
class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='recipes/')

    def __str__(self):
        return self.name
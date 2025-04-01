from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe

class ChefSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)  

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
         

class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)  

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'image']
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, ChefProfile

class ChefSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)  

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ChefProfile
        fields = ['profile_picture']  
         

class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)  

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'image']
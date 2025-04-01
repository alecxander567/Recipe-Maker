from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import ChefSignUpForm, UserSignUpForm, RecipeForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import UserAccount, Recipe
from django.urls import reverse
from django.contrib.auth.decorators import login_required


# Landingpage
def landingpage(request):
    return render(request, 'landingpage.html')


@login_required
def chef_homepage(request):
    return render(request, "chefhomepage.html") 


@login_required
def user_homepage(request):
    return render(request, "userhomepage.html") 


# Chef sign up
def chef_signup(request):
    if request.method == "POST":
        form = ChefSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            login(request, user)  
            return redirect("chef_homepage")
        else:
            return render(request, "landingpage.html", {"form": form, "errors": form.errors})   
    else:
        form = ChefSignUpForm()

    return render(request, "landingpage.html", {"form": form})


# Chef Log in
def chef_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.filter(email=email).first()
        
        if user and authenticate(request, username=user.username, password=password):
            login(request, user)
            return redirect("chef_homepage")
        else:
            return render(request, "landingpage.html", {"error": "Invalid email or password"})

    return render(request, "landingpage.html")


# User sign up 
def user_signup(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print(f"✅ Logged in user: {user}")
            return redirect("user_homepage")  
        else:
            print(f"❌ Signup errors: {form.errors}")
            return render(request, "landingpage.html", {"form": form, "errors": form.errors})
    else:
        form = UserSignUpForm()
    
    return render(request, "landingpage.html", {"form": form})


# User log in
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.filter(email=email).first()
        if user and authenticate(request, username=user.username, password=password):
            login(request, user)
            return redirect("user_homepage")  # Redirect to user homepage
        else:
            return render(request, "landingpage.html", {"error": "Invalid email or password"})

    return render(request, "landingpage.html")


# Adding recipe function
@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('chef_homepage')  # Change to the appropriate URL
    else:
        form = RecipeForm()
    return render(request, 'chefhomepage.html', {'form': form})


def get_recipes(request):
    recipes = Recipe.objects.all().values('id', 'name', 'description', 'image')
    return JsonResponse(list(recipes), safe=False)


# Log out view
def user_logout(request):
    logout(request)
    return redirect('landingpage') 





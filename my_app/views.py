from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import ChefSignUpForm, UserSignUpForm, RecipeForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Recipe
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


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
            return redirect("user_homepage")  
        else:
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
            return redirect("user_homepage") 
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
            return redirect('chef_homepage')
    else:
        form = RecipeForm()
    return render(request, 'chefhomepage.html', {'form': form})


def get_recipes(request):
    recipes = Recipe.objects.all().values('id', 'name', 'description', 'image')
    return JsonResponse(list(recipes), safe=False)


# Edit Recipe
@csrf_exempt
def edit_recipe(request, recipe_id):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.name = request.POST.get("name")
        recipe.description = request.POST.get("description")

        if "image" in request.FILES:
            recipe.image = request.FILES["image"]

        recipe.save()
        return JsonResponse({"success": True})
    
    return JsonResponse({"success": False, "error": "Invalid request method"})


# Log out view
def user_logout(request):
    logout(request)
    return redirect('landingpage') 





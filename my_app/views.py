from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import ChefSignUpForm, UserSignUpForm, RecipeForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Recipe, UserAccount
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .forms import ProfileUpdateForm
from django.core.exceptions import ObjectDoesNotExist


# Landingpage
def landingpage(request):
    return render(request, 'landingpage.html')


# Chef homepage
@login_required
def chef_homepage(request):
    chef_profile = request.user.chefprofile

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=chef_profile)

        if 'remove_picture' in request.POST:
            chef_profile.profile_picture.delete()
            chef_profile.save()
            return redirect('chef_homepage')
        elif form.is_valid():
            form.save()
            return redirect('chef_homepage')

    else:
        form = ProfileUpdateForm(instance=chef_profile)

    return render(request, 'chefhomepage.html', {'form': form, 'chef_profile': chef_profile})


# User homepage
@login_required
def user_homepage(request):
    try:
        user_account = UserAccount.objects.get(user=request.user)
    except ObjectDoesNotExist:
        user_account = UserAccount.objects.create(user=request.user)

    if request.method == 'POST' and request.FILES.get('profile_picture'):
        user_account.profile_picture = request.FILES['profile_picture']
        user_account.save()
        return redirect('user_homepage')
    
    if request.method == 'POST' and 'remove_picture' in request.POST:
        user_account.profile_picture = None
        user_account.save()
        return redirect('user_homepage')

    return render(request, 'userhomepage.html', {'user_account': user_account})


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


# Display recipes
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


# Delete recipe function
def delete_recipe(request, recipe_id):
    if request.method == "DELETE":
        try:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            recipe.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})


# Log out view
def user_logout(request):
    logout(request)
    return redirect('landingpage') 





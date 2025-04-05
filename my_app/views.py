from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import ChefSignUpForm, UserSignUpForm, RecipeForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Recipe, UserAccount, ChefProfile, FavoriteRecipe
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .forms import ProfileUpdateForm
from django.contrib import messages


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
    user_account = None
    chef_profile = None
    is_regular_user = False
    is_chef = False

    if request.user.is_authenticated:
        try:
            user_account = UserAccount.objects.get(user=request.user)
            is_regular_user = True
        except UserAccount.DoesNotExist:
            pass

        try:
            chef_profile = ChefProfile.objects.get(user=request.user)
            is_chef = True
        except ChefProfile.DoesNotExist:
            pass

    recipes = []
    if chef_profile:
        recipes = Recipe.objects.filter(chef=chef_profile)
    else:
        recipes = Recipe.objects.all()

    if request.method == 'POST' and 'add_to_favorites' in request.POST:
        recipe_id = request.POST.get('recipe_id')
        recipe = Recipe.objects.get(id=recipe_id)

        # Ensure the user is logged in
        if user_account:
            FavoriteRecipe.objects.create(user=user_account, recipe=recipe)
            messages.success(request, 'Recipe added to favorites successfully!')

        return redirect('user_homepage') 

    favorite_recipes = FavoriteRecipe.objects.filter(user=user_account)

    if request.method == 'POST' and request.FILES.get('profile_picture'):
        if user_account:
            user_account.profile_picture = request.FILES['profile_picture']
            user_account.save()
        return redirect('user_homepage')

    if request.method == 'POST' and 'remove_picture' in request.POST:
        if user_account:
            user_account.profile_picture = None
            user_account.save()
        return redirect('user_homepage')

    # Determine user details for display
    if is_regular_user:
        display_name = user_account.username
        display_email = user_account.email 
    elif is_chef:
        display_name = chef_profile.full_name
        display_email = "" 
    else:
        display_name = "Unknown"
        display_email = ""

    context = {
        'user_account': user_account,
        'chef_profile': chef_profile,
        'recipes': recipes,
        'favorite_recipes': favorite_recipes,
        'is_regular_user': is_regular_user,
        'is_chef': is_chef,
        'display_name': display_name,
        'display_email': display_email,
    }

    return render(request, 'userhomepage.html', context)


    
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


# Delete a favorite recipe
def delete_favorite(request):
    if request.method == 'POST':
        if request.POST.get('_method') == 'DELETE':
            recipe_id = request.POST.get('recipe_id')
            
            recipe = get_object_or_404(Recipe, id=recipe_id)

            if request.user.is_authenticated:
                try:
                    user_account = UserAccount.objects.get(user=request.user)
                    
                    favorite_recipe = FavoriteRecipe.objects.filter(user=user_account, recipe=recipe).first()
                    
                    if favorite_recipe:
                        favorite_recipe.delete() 
                        messages.success(request, "Recipe removed from favorites.")
                    else:
                        messages.error(request, "This recipe is not in your favorites.")
                except UserAccount.DoesNotExist:
                    messages.error(request, "User account not found.")
            else:
                messages.error(request, "You must be logged in to remove favorites.")

        else:
            messages.error(request, "Invalid method for deleting the favorite.")

        return redirect('user_homepage')
    

# Log out view
def user_logout(request):
    logout(request)
    return redirect('landingpage') 





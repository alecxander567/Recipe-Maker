from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import ChefSignUpForm, UserSignUpForm, RecipeForm, ProfileUpdateForm 
from .models import Recipe, UserAccount, FavoriteRecipe, Rating
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
import json

# Landingpage
def landingpage(request):
    return render(request, 'landingpage.html')


# Chef homepage
@login_required
def chef_homepage(request):
    try:
        user_account = request.user.useraccount
        if user_account.role != 'chef':
            raise ValueError("User is not a chef")
    except UserAccount.DoesNotExist:
        return redirect('landingpage')
    except ValueError:
        return redirect('landingpage')

    chef_recipes = Recipe.objects.filter(chef=user_account)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_account)

        if 'remove_picture' in request.POST:
            if user_account.profile_picture:
                user_account.profile_picture.delete()
                user_account.save()
                messages.success(request, 'Profile picture removed successfully!')
            return redirect('chef_homepage')

        elif form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('chef_homepage')

    else:
        form = ProfileUpdateForm(instance=user_account)

    return render(request, 'chefhomepage.html', {
        'chef_recipes': chef_recipes,
        'user_account': user_account,
        'form': form, 
    })
    
    
# User homepage
@login_required
def user_homepage(request):
    user_account = None
    is_regular_user = False
    is_chef = False
    chef_profile = None

    if request.user.is_authenticated:
        try:
            user_account = UserAccount.objects.get(user=request.user)
            is_regular_user = True
            if user_account.role == 'chef':
                is_chef = True
        except UserAccount.DoesNotExist:
            pass

    recipes = []
    if is_chef:
        recipes = Recipe.objects.filter(chef=user_account)
    else:
        recipes = Recipe.objects.all()

    if request.method == 'POST' and 'add_to_favorites' in request.POST:
        recipe_id = request.POST.get('recipe_id')
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            if user_account:
                FavoriteRecipe.objects.create(user=user_account, recipe=recipe)
                messages.success(request, 'Recipe added to favorites successfully!')
        except Recipe.DoesNotExist:
            messages.error(request, 'Recipe not found.')
        return redirect('user_homepage')

    favorite_recipes = FavoriteRecipe.objects.filter(user=user_account)

    if request.method == 'POST':
        if request.FILES.get('profile_picture'):
            if user_account:
                user_account.profile_picture = request.FILES['profile_picture']
                user_account.save()
                messages.success(request, 'Profile picture updated successfully!')
        elif 'remove_picture' in request.POST:
            if user_account:
                user_account.profile_picture = None
                user_account.save()
                messages.success(request, 'Profile picture removed successfully!')

        return redirect('user_homepage')

    if is_regular_user:
        display_name = user_account.user.username
    elif is_chef:
        display_name = user_account.user.username
    else:
        display_name = "Unknown"

    display_email = request.user.email

    context = {
        'user_account': user_account,
        'recipes': recipes,
        'favorite_recipes': favorite_recipes,
        'is_regular_user': is_regular_user,
        'is_chef': is_chef,
        'display_name': display_name,
        'display_email': display_email,
    }

    return render(request, 'userhomepage.html', context)


# Chef sign up function
def chef_signup(request):
    if request.method == "POST":
        form = ChefSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('chef_homepage')
    else:
        form = ChefSignUpForm()

    return render(request, 'landingpage.html', {'form': form})


# Chef Log in function
def chef_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.filter(email=email).first()

        if user and authenticate(request, username=user.username, password=password):
            try:
                user_account = UserAccount.objects.get(user=user)
                if user_account.role == "chef":
                    login(request, user)
                    return redirect("chef_homepage")
                else:
                    return render(request, "landingpage.html", {
                        "error": "Access denied: This account is not a chef."
                    })
            except UserAccount.DoesNotExist:
                return render(request, "landingpage.html", {
                    "error": "User account not found."
                })
        else:
            return render(request, "landingpage.html", {
                "error": "Invalid email or password"
            })

    return render(request, "landingpage.html")


# User sign up function
def user_signup(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            if UserAccount.objects.filter(user__email=user.email).exists():
                return render(request, "landingpage.html", {"form": form, "error": "Email already in use"})

            UserAccount.objects.create(user=user, role='user')
            
            login(request, user)

            return redirect("user_homepage")
        else:
            return render(request, "landingpage.html", {"form": form, "errors": form.errors})
    else:
        form = UserSignUpForm()

    return render(request, "landingpage.html", {"form": form})


# User Log in function
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.filter(email=email).first()

        if user and authenticate(request, username=user.username, password=password):
            if hasattr(user, 'useraccount') and user.useraccount.role == 'user':
                login(request, user)
                return redirect('user_homepage')
            else:
                return render(request, "landingpage.html", {"error": "Not a regular user account."})
        else:
            return render(request, "landingpage.html", {"error": "Invalid email or password"})

    return render(request, "landingpage.html")


@login_required
def add_recipe(request):
    try:
        user_account = request.user.useraccount
        if user_account.role != 'chef':
            raise ValueError("User is not a chef")
    except UserAccount.DoesNotExist:
        return redirect('landingpage')
    except ValueError:
        return redirect('landingpage')

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.chef = user_account
            recipe.save()
            return redirect('chef_homepage')  # ✅ Redirect to home after POST
    else:
        form = RecipeForm()

    return render(request, 'chefhomepage.html', {'form': form})  # ✅


# Display recipes
@login_required
def get_recipes(request):
    user_account = request.user.useraccount

    if user_account.role == 'chef':
        recipes = Recipe.objects.filter(chef=user_account).values('id', 'name', 'description', 'image')
        return JsonResponse(list(recipes), safe=False)
    else:
        return JsonResponse({'error': 'You are not authorized to view recipes'}, status=403)


@login_required
def edit_recipe(request, recipe_id):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, id=recipe_id)

        # Check if user is authorized
        try:
            user_account = UserAccount.objects.get(user=request.user)
            if user_account.role != 'chef':
                return JsonResponse({"success": False, "error": "You must be a chef to edit recipes."})
        except UserAccount.DoesNotExist:
            return JsonResponse({"success": False, "error": "User account not found."})

        if recipe.chef != user_account:
            return JsonResponse({"success": False, "error": "You cannot edit a recipe that is not yours."})

        # Update recipe fields
        recipe.name = request.POST.get("name")
        recipe.description = request.POST.get("description")

        if "image" in request.FILES:
            recipe.image = request.FILES["image"]

        recipe.save()

        return JsonResponse({"success": True, "message": "Recipe updated successfully!"})

    return JsonResponse({"success": False, "error": "Invalid request method"})


# Delete recipe function
@login_required
def delete_recipe(request, recipe_id):
    if request.method == "DELETE":
        recipe = get_object_or_404(Recipe, id=recipe_id)

        try:
            user_account = UserAccount.objects.get(user=request.user)
            if user_account.role != 'chef':
                return JsonResponse({"success": False, "error": "You must be a chef to delete recipes."})

            if recipe.chef != user_account:
                return JsonResponse({"success": False, "error": "You cannot delete a recipe that is not yours."})
            
            recipe.delete()
            return JsonResponse({"success": True})

        except UserAccount.DoesNotExist:
            return JsonResponse({"success": False, "error": "User account not found."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})


# Delete a favorite recipe
@login_required
def delete_favorite(request):
    if request.method == 'POST':
        if request.POST.get('_method') == 'DELETE':
            recipe_id = request.POST.get('recipe_id')
        
            recipe = get_object_or_404(Recipe, id=recipe_id)

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
            messages.error(request, "Invalid method for deleting the favorite.")

        return redirect('user_homepage')

    return JsonResponse({"success": False, "error": "Invalid request method."})
    
    
# view chefs function
def get_chefs(request):
    chefs = UserAccount.objects.filter(role='chef').select_related('user').values('user__username', 'user__email', 'profile_picture')
    
    for chef in chefs:
        if chef["profile_picture"]:
            chef['profile_picture'] = f'/media/{chef["profile_picture"]}'
        else:
            chef['profile_picture'] = None 

        chef['full_name'] = chef['user__username']

    return JsonResponse({'chefs': list(chefs)})


# Get chef recipes 
def get_chef_recipes(request, chef_name):
    try:
        user_account = UserAccount.objects.get(user__username=chef_name)
        
        recipes = user_account.recipes.all()

        if not recipes:
            return JsonResponse({'error': 'No recipes found for this chef'}, status=404)

        recipe_data = []
        for recipe in recipes:
            recipe_data.append({
                'id': recipe.id,
                'name': recipe.name,
                'image_url': recipe.image.url,
                'description': recipe.description,
                'average_rating': recipe.average_rating if recipe.average_rating else "Not Rated Yet",
            })

        return JsonResponse({'recipes': recipe_data})
    
    except UserAccount.DoesNotExist:
        return JsonResponse({'error': 'Chef not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
@csrf_exempt
def rate_recipe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            recipe_id = data.get('recipeId')
            rating_value = int(data.get('rating', 0))

            recipe = Recipe.objects.get(id=recipe_id)

            Rating.objects.create(recipe=recipe, value=rating_value)

            ratings = recipe.ratings.all()

            average = round(sum(r.value for r in ratings) / ratings.count(), 1)

            return JsonResponse({'average': average})

        except Recipe.DoesNotExist:
            return JsonResponse({'error': 'Recipe not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': 'Invalid request'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


# Get the most trend recipes(regular users view)
def get_trending_recipes(request):
    recipes = Recipe.objects.annotate(
        avg_rating=Avg('ratings__value')
    ).order_by('-avg_rating')[:10]

    data = {
        'recipes': [
            {
                'id': recipe.id,
                'name': recipe.name,
                'description': recipe.description,
                'image_url': recipe.image.url if recipe.image else '',
                'average_rating': round(recipe.avg_rating, 1) if recipe.avg_rating else None
            }
            for recipe in recipes
        ]
    }

    return JsonResponse(data)


# Get the top rated recipes(Chef's view)
def get_top_rated_recipes(request):
    top_rated_recipes = Recipe.objects.annotate(avg_rating=Avg('ratings__value')).order_by('-avg_rating')[:5]

    recipes_data = [{
        'name': recipe.name,
        'average_rating': round(recipe.avg_rating, 1) if recipe.avg_rating else None,
        'image': recipe.image.url if recipe.image else None,
    } for recipe in top_rated_recipes]

    return JsonResponse({'recipes': recipes_data})


# View regular users function
def get_users(request):
    # Fetch all regular users (role='user')
    users = UserAccount.objects.filter(role='user').select_related('user').values('user__username', 'user__email', 'profile_picture')
    
    # Loop through users to handle profile pictures
    for user in users:
        if user["profile_picture"]:
            user['profile_picture'] = f'/media/{user["profile_picture"]}'
        else:
            user['profile_picture'] = None  # Use a default profile picture if no image exists

        user['full_name'] = user['user__username']  # We assume the username is the full name

    return JsonResponse({'users': list(users)})
    
    
# Log out view
def user_logout(request):
    logout(request)
    return redirect('landingpage') 





from django.urls import path
from .views import landingpage, chef_signup, chef_login, chef_homepage, user_signup, user_login, user_homepage, user_logout, add_recipe, get_recipes, edit_recipe, delete_recipe, delete_favorite, get_chefs, get_chef_recipes, rate_recipe, get_trending_recipes, get_top_rated_recipes, get_users

urlpatterns = [
    path('', landingpage, name='home'),
    path('landingpage/', landingpage, name='landingpage'),
    path('chef-signup/', chef_signup, name='chef_signup'),
    path("chef-login/", chef_login, name="chef_login"),
    path("chef-homepage/", chef_homepage, name="chef_homepage"),
    path('signup/', user_signup, name='user_signup'),
    path("user-login/", user_login, name="user_login"),
    path("user-homepage/", user_homepage, name="user_homepage"),
    path('add-recipe/', add_recipe, name='add_recipe'),
    path('api/recipes/', get_recipes, name='get_recipes'),
    path("edit-recipe/<int:recipe_id>/", edit_recipe, name="edit_recipe"),
    path('delete-recipe/<int:recipe_id>/', delete_recipe, name='delete_recipe'),
    path('delete-favorite/', delete_favorite, name='delete_favorite'),
    path('get-chefs/', get_chefs, name='get_chefs'),
    path('get_chef_recipes/<str:chef_name>/', get_chef_recipes, name='get_recipes'),
    path('rate-recipe/', rate_recipe, name='rate_recipe'),
    path('get_trending_recipes/', get_trending_recipes, name='get_trending_recipes'),
    path('get_top_rated_recipes/', get_top_rated_recipes, name='get_top_rated_recipes'),
    path('get-users/', get_users, name='get_users'),
    path('logout/', user_logout, name='logout'),  
]

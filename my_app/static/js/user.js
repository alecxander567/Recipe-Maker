window.addEventListener("load", function () {
    document.getElementById("loader").style.display = "none";
});

function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('active');
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    }); 
  }

const recipeRatings = {};
const chefsModal = document.getElementById('chefsModal');

function toggleDescription(recipeId) {
    var descElement = document.getElementById('desc-' + recipeId);
    var recipeCard = descElement.closest('.recipe-card');
        
    if (descElement.style.display === "none") {
        descElement.style.display = "block";  
        recipeCard.style.height = 'auto';  
    } else {
        descElement.style.display = "none"; 
        recipeCard.style.height = '';  
    }
}

function showFavoritesModal() {
    var myModal = new bootstrap.Modal(document.getElementById('favoritesModal'));
    myModal.show();
}

chefsModal.addEventListener('show.bs.modal', function () {
    fetch('/get-chefs/')
        .then(response => response.json())
        .then(data => {
            console.log("Fetched chefs:", data); 
            const body = document.getElementById('chefsModalBody');
            if (data.chefs.length > 0) {
                let html = '<div class="list-group">';
                data.chefs.forEach(chef => {
                    console.log("Chef:", chef);
                    html += `
                        <div class="d-flex justify-content-between align-items-center border rounded p-2 mb-2">
                            <div class="d-flex align-items-center">
                                <img src="${chef.profile_picture}" alt="${chef.full_name}" class="rounded-circle me-3" style="width: 50px; height: 50px; object-fit: cover;">
                                <strong>Chef ${chef.full_name}</strong>
                            </div>
                            <button class="btn btn-sm btn-success" onclick="viewRecipes('${chef.full_name}')">View Recipes</button>
                        </div>
                    `;
                });
                html += '</div>';
                body.innerHTML = html;
            } else {
                body.innerHTML = 'No chefs found.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('chefsModalBody').innerHTML = 'Error loading chefs.';
        });
});
    
function viewRecipes(chefName) {
    fetch(`/get_chef_recipes/${chefName}/`)
        .then(response => response.json())
        .then(data => {
            const recipeContainer = document.getElementById('recipeContainer');
            if (data.recipes.length > 0) {
                let html = '';
                data.recipes.forEach(recipe => {
                    const averageRating = recipe.average_rating ? recipe.average_rating : "No ratings yet";    
                    html += `
                        <div class="recipe-card">
                            <img src="${recipe.image_url}" class="recipe-card-img" alt="${recipe.name}">
                            <div class="recipe-card-body">
                            <h5 class="recipe-card-title">${recipe.name}</h5>
                                <p class="overall-rating" id="rating-${recipe.id}" style="color: white;">
                                    ${averageRating} ★
                                </p>
                                <p class="recipe-card-description" id="desc-${recipe.id}" style="display: none;">${recipe.description}</p>
                                <button class="btn btn-success w-100" onclick="toggleDescription(${recipe.id})">
                                    View Full Recipe
                                </button>
                                <div class="recipe-card-actions d-flex flex-column gap-2 mt-2">
                                    <form action="{% url 'user_homepage' %}" method="POST">
                                        {% csrf_token %}
                                        <input type="hidden" name="recipe_id" value="${recipe.id}">
                                        <button type="submit" name="add_to_favorites" class="btn btn-warning w-100">Add to Favorites</button>
                                    </form>
                                    <button class="btn btn-info w-100" onclick="rateRecipe('${recipe.id}')">Rate Recipe</button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                recipeContainer.innerHTML = html;
            } else {
                recipeContainer.innerHTML = '<p>No recipes available for this chef.</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('recipeContainer').innerHTML = 'Error loading recipes.';
        });
}

function getCSRFToken() {
    let csrfToken = null;
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfTokenElement) {
        csrfToken = csrfTokenElement.value;
    }
    return csrfToken;
}

function rateRecipe(recipeId) {
    const numericRating = prompt(`Rate this recipe from 1 to 5:`);

    if (!numericRating || isNaN(numericRating) || numericRating < 1 || numericRating > 5) {
        alert('Please enter a valid number between 1 and 5.');
        return;
    }

    const csrfToken = getCSRFToken(); 

    if (!csrfToken) {
        console.error("CSRF token is missing");
        return;
    }

    fetch('/rate-recipe/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken 
        },
        body: JSON.stringify({
            recipeId: recipeId,
            rating: numericRating
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.average) {
            console.log(`New average rating: ${data.average}`);
            document.getElementById(`rating-${recipeId}`).innerText = `${data.average} ★`;
        } else {
            console.log('Error:', data.error);
        }
    })
    .catch(error => console.log('Request failed', error));
}

function viewTrendingRecipes() {
    fetch('/get_trending_recipes/')
        .then(response => response.json())
        .then(data => {
            const recipeContainer = document.getElementById('recipeContainer');
            if (data.recipes.length > 0) {
                let html = '';
                data.recipes.forEach(recipe => {
                    const ratingText = recipe.average_rating ? `${recipe.average_rating} ★` : "No ratings yet ★";
                    html += `
                        <div class="recipe-card">
                            <img src="${recipe.image_url}" class="recipe-card-img" alt="${recipe.name}">
                            <div class="recipe-card-body">
                                <h5 class="recipe-card-title">${recipe.name}</h5>
                                <p class="overall-rating" style="color: white;">${ratingText}</p>
                                <p class="recipe-card-description" id="desc-${recipe.id}" style="display: none;">${recipe.description}</p>
                                <button class="btn btn-success w-100" onclick="toggleDescription(${recipe.id})">
                                    View Full Recipe
                                </button>
                                <div class="recipe-card-actions d-flex flex-column gap-2 mt-2">
                                    <form action="{% url 'user_homepage' %}" method="POST">
                                        {% csrf_token %}
                                        <input type="hidden" name="recipe_id" value="${recipe.id}">
                                        <button type="submit" name="add_to_favorites" class="btn btn-warning w-100">Add to Favorites</button>
                                    </form>
                                    <button class="btn btn-info w-100" onclick="rateRecipe(${recipe.id})">Rate Recipe</button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                recipeContainer.innerHTML = html;
            } else {
                recipeContainer.innerHTML = '<p>No trending recipes found.</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('recipeContainer').innerHTML = '<p>Error loading trending recipes.</p>';
        });
}

usersModal.addEventListener('show.bs.modal', function () {
    fetch('/get-users/') 
        .then(response => response.json())
        .then(data => {
            
            const body = document.getElementById('usersModalBody');  
            
            if (data.users.length > 0) { 
                let html = '<div class="list-group">'; 
                data.users.forEach(user => {
                    console.log("User:", user);

                    const profilePicture = user.profile_picture ? user.profile_picture : '/static/img/user-icon.avif';

                    html += `
                        <div class="d-flex justify-content-between align-items-center border rounded p-2 mb-2">
                            <div class="d-flex align-items-center">
                                <img src="${profilePicture}" alt="${user.full_name}'s Profile" class="rounded-circle me-3" style="width: 50px; height: 50px; object-fit: cover;">
                                <strong>${user.full_name}</strong> 
                            </div>
                        </div>
                    `;
                });
                html += '</div>'; 
                body.innerHTML = html; 
            } else {
                body.innerHTML = 'No users found.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('usersModalBody').innerHTML = 'Error loading users.';
        });
});

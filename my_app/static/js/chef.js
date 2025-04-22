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

let ratingChart = null;

document.addEventListener("DOMContentLoaded", function () {
  fetchRecipes();

  document.getElementById("recipeContainer").addEventListener("click", function (event) {
      if (event.target.classList.contains("delete-btn")) {
          const recipeCard = event.target.closest(".recipe-card");
          const recipeId = event.target.getAttribute("data-id");
          
          if (!recipeCard || !recipeId) {
              console.error("Recipe card or ID not found.");
              return;
          }

          if (confirm("Are you sure you want to delete this recipe?")) {
              fetch(`/delete-recipe/${recipeId}/`, {
                  method: "DELETE",
                  headers: {
                      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                  }
              })
              .then(response => response.json())
              .then(data => {
                  if (data.success) {
                      alert("Recipe deleted successfully!");
                      recipeCard.remove();
                  } else {
                      alert("Failed to delete recipe.");
                  }
              })
              .catch(error => {
                  alert("An error occurred while deleting the recipe.");
              });
          }
      }
  });

  document.getElementById("recipeContainer").addEventListener("click", function (event) {
      if (event.target.classList.contains("view-recipe-btn")) {
          const recipeCard = event.target.closest(".recipe-card");
          const description = recipeCard.querySelector(".recipe-card-description");

          recipeCard.classList.toggle("expanded");

          if (description.style.display === "none" || description.style.display === "") {
              description.style.display = "block";
              event.target.textContent = "Hide Recipe";
          } else {
              description.style.display = "none";
              event.target.textContent = "View Recipe";
          }
      }

      if (event.target.classList.contains("edit-recipe-btn")) {
          const recipeCard = event.target.closest(".recipe-card");
          if (!recipeCard) {
              return;
          }

          const recipeId = recipeCard.dataset.id;
          const recipeName = recipeCard.querySelector(".recipe-card-title").textContent;
          const recipeDescription = recipeCard.querySelector(".recipe-card-description").textContent;

          document.getElementById("editRecipeId").value = recipeId;
          document.getElementById("editRecipeName").value = recipeName;
          document.getElementById("editRecipeDescription").value = recipeDescription;

          let editModal = new bootstrap.Modal(document.getElementById("editRecipeModal"));
          editModal.show();
      }
  });

  document.getElementById("editRecipeForm").addEventListener("submit", function (event) {
      event.preventDefault();

      let formData = new FormData(this);
      let recipeId = document.getElementById("editRecipeId").value;

      for (let pair of formData.entries()) {
          console.log(pair[0] + ": " + pair[1]);
      }

      fetch(`/edit-recipe/${recipeId}/`, {
          method: "POST",
          body: formData,
          headers: {
              "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
          }
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              alert("Recipe updated successfully!");
              location.reload();
          } else {
              alert("Failed to update recipe: " + (data.error || "Unknown error"));
          }
      })
      .catch(error => console.error("Error:", error));
  });
});

function fetchRecipes() {
  console.log("Fetching recipes...");
  fetch('/api/recipes/')
      .then(response => {
          console.log("Response received:", response);
          return response.json();
      })
      .then(data => {
          console.log("Recipes data:", data);
          let container = document.getElementById("recipeContainer");
          container.innerHTML = "";
          data.forEach(recipe => {
              let recipeCard = `
                  <div class="recipe-card" data-id="${recipe.id}">
                      <img src="${recipe.image ? '/media/' + recipe.image : '/static/default.jpg'}" class="recipe-card-img" alt="${recipe.name}">
                      <div class="recipe-card-body">
                          <h6 class="recipe-card-title">${recipe.name}</h6>
                          <p class="recipe-card-description" style="display: none;">${recipe.description}</p>
                      </div>
                      <div class="recipe-card-actions">
                          <button class="btn btn-info view-recipe-btn text-white">View Recipe</button>
                          <button class="btn btn-success text-white edit-recipe-btn">Edit Recipe</button>
                          <button class="btn btn-danger delete-btn" data-id="${recipe.id}">Delete</button>
                      </div>
                  </div>
              `;
              container.innerHTML += recipeCard;
          });
      })
  .catch(error => console.error("Error fetching recipes:", error));
}


document.getElementById('topRatedBtn').addEventListener('click', function() {
  console.log('Top Rated button clicked');
  
  fetch('/get_top_rated_recipes/')
      .then(response => response.json())
      .then(data => {
          console.log('Data received:', data);
          const recipes = data.recipes;
          const labels = recipes.map(recipe => recipe.name);
          const ratings = recipes.map(recipe => recipe.average_rating);

          const ctx = document.getElementById('ratingChart').getContext('2d');
          const ratingChart = new Chart(ctx, {
              type: 'bar',
              data: {
                  labels: labels,
                  datasets: [{
                      label: 'Ratings',
                      data: ratings,
                      backgroundColor: 'rgba(34, 139, 34, 0.2)',
                      borderColor: 'rgba(34, 139, 34, 1)',
                      borderWidth: 1
                  }]
              },
              options: {
                  scales: {
                      y: {
                          beginAtZero: true
                      }
                  }
              }
          });

          const recipesContainer = document.getElementById('topRatedRecipesContainer');
          recipesContainer.innerHTML = '';

          recipes.forEach(recipe => {
              const recipeItem = document.createElement('div');
              recipeItem.classList.add('recipe-item');

              const img = document.createElement('img');
              img.src = recipe.image;
              img.alt = recipe.name;

              const recipeDetails = document.createElement('div');
              recipeDetails.innerHTML = `<strong>${recipe.name}</strong><br><span>Rating: ${recipe.average_rating}</span>`;

              recipeItem.appendChild(img);
              recipeItem.appendChild(recipeDetails);

              recipesContainer.appendChild(recipeItem);
          });

          const modal = new bootstrap.Modal(document.getElementById('topRatedModal'));
          modal.show();
      })
      .catch(error => {
          console.error('Error fetching top-rated recipes:', error);
      });
});
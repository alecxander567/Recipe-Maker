document.addEventListener("DOMContentLoaded", function () {
    // Fetch recipes and render them
    fetchRecipes();

    document.getElementById("recipeContainer").addEventListener("click", function (event) {
        if (event.target.classList.contains("delete-btn")) {
            const recipeCard = event.target.closest(".recipe-card");
            const recipeId = event.target.getAttribute("data-id");
            
            if (!recipeCard || !recipeId) {
                console.error("Recipe card or ID not found.");
                return;
            }

            // Confirm the delete action
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

    // Event delegation for dynamically added buttons (delete, edit, view)
    document.getElementById("recipeContainer").addEventListener("click", function (event) {
        // View Recipe button functionality
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

        // Edit Recipe button functionality
        if (event.target.classList.contains("edit-recipe-btn")) {
            const recipeCard = event.target.closest(".recipe-card");
            if (!recipeCard) {
                return;
            }

            const recipeId = recipeCard.dataset.id;
            const recipeName = recipeCard.querySelector(".recipe-card-title").textContent;
            const recipeDescription = recipeCard.querySelector(".recipe-card-description").textContent;

            console.log("Recipe ID:", recipeId);
            console.log("Recipe Name:", recipeName);
            console.log("Recipe Description:", recipeDescription);

            document.getElementById("editRecipeId").value = recipeId;
            document.getElementById("editRecipeName").value = recipeName;
            document.getElementById("editRecipeDescription").value = recipeDescription;

            let editModal = new bootstrap.Modal(document.getElementById("editRecipeModal"));
            editModal.show();
        }
    });

    // Edit Recipe Form submission
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

// Fetch recipes and render them in the container
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


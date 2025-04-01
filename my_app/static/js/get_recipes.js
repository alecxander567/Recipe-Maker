document.addEventListener("DOMContentLoaded", function() {
    fetchRecipes();
});

function fetchRecipes() {
    fetch('/api/recipes/')  
    .then(response => response.json())
    .then(data => {
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
                        <button class="btn btn-danger delete-recipe-btn">Delete Recipe</button>
                    </div>
                </div>
                `;
            container.innerHTML += recipeCard;
        });
    })
    .catch(error => console.error("Error fetching recipes:", error));
}

document.addEventListener("DOMContentLoaded", function () {
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
    });
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

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("recipeContainer").addEventListener("click", function (event) {

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
});



   

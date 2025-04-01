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
                <div class="recipe-card">
                    <img src="${recipe.image ? '/media/' + recipe.image : '/static/default.jpg'}" class="recipe-card-img" alt="${recipe.name}">
                    <div class="recipe-card-body">
                    <h6 class="recipe-card-title">${recipe.name}</h6>
                    <p class="recipe-card-description" style="display: none;">${recipe.description}</p>
                    </div>
                    <div class="recipe-card-actions">
                        <button class="btn btn-info view-recipe-btn text-white">View Recipe</button>
                        <button class="btn btn-success text-white">Edit Recipe</button>
                        <button class="btn btn-danger">Delete Recipe</button>
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



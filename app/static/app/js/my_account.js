const mealPlanKey = "userMealPlan";
document.addEventListener("DOMContentLoaded", function () {
    // Kích hoạt tab menu
    let tabLinks = document.querySelectorAll('.account-settings-links a');
    tabLinks.forEach(function (tab) {
        tab.addEventListener("click", function (e) {
            e.preventDefault();
            let activeLink = document.querySelector('.account-settings-links .active');
            if (activeLink) activeLink.classList.remove("active");

            let activePane = document.querySelector('.tab-pane.active');
            if (activePane) activePane.classList.remove("active", "show");

            this.classList.add("active");
            let targetPane = document.querySelector(this.getAttribute("href"));
            if (targetPane) targetPane.classList.add("active", "show");
        });
    });
// Load lại dữ liệu đã lưu
    loadSavedMeals(mealPlanKey);
});


function saveMeals(day, mealType) {
    let selects = document.querySelectorAll(`#meal-container-${day}-${mealType} select`);
    let selectedMeals = [];

    selects.forEach(select => {
        if (select.value) {
            selectedMeals.push(select.value);
        }
    });

    console.log(`🛠 [DEBUG] Saving ${mealType} for ${day}:`, selectedMeals);



    let mealPlan = JSON.parse(localStorage.getItem(mealPlanKey)) || {};
    if (!mealPlan[day]) {
        mealPlan[day] = {};
    }
    mealPlan[day][mealType] = selectedMeals;

    localStorage.setItem(mealPlanKey, JSON.stringify(mealPlan));
    console.log(`📁 [DEBUG] localStorage updated:`, localStorage.getItem(mealPlanKey));

    updateMealDisplay(day, mealType, mealPlanKey);
}


// Hiển thị danh sách món đã chọn
function updateMealDisplay(day, mealType, mealPlanKey) {
    let mealPlan = JSON.parse(localStorage.getItem(mealPlanKey)) || {};
    let selectedMeals = mealPlan[day] && mealPlan[day][mealType] ? mealPlan[day][mealType] : [];
    let displayElement = document.getElementById(`selected-meals-${day}-${mealType}`);

    if (displayElement) {
        displayElement.textContent = selectedMeals.length > 0 ?  selectedMeals.join(", ") : "Chưa có món";
    }
}

// Load dữ liệu đã lưu sau khi refresh
function loadSavedMeals(mealPlanKey) {
    let mealPlan = JSON.parse(localStorage.getItem(mealPlanKey)) || {};

    for (let day in mealPlan) {
        for (let mealType in mealPlan[day]) {
            mealPlan[day][mealType].forEach(mealId => {
                addMealSelect(day, mealType, mealId);
            });
            updateMealDisplay(day, mealType, mealPlanKey);
        }
    }
}


function addMealSelect(day, mealType, selectedValue = "") {
    let container = document.getElementById(`meal-container-${day}-${mealType}`);
    if (!container) {
        console.error("Không tìm thấy container:", `meal-container-${day}-${mealType}`);
        return;
    }

    let newSelect = document.createElement("div");
    newSelect.classList.add("meal-select");

    let selectHTML = `<select name="meal_${day}_${mealType}" required><option value="">Chọn món</option>`;

    if (!Array.isArray(productCategories)) {
        console.error("Dữ liệu productCategories không hợp lệ:", productCategories);
        return;
    }

    productCategories.forEach(category => {
        selectHTML += `<optgroup label="${category.name}">`;
        if (Array.isArray(category.products)) {
            category.products.forEach(product => {
                selectHTML += `<option value="${product.id}" ${selectedValue == product.id ? "selected" : ""}>
                                ${product.name} (${product.calories} kcal)
                              </option>`;
            });
        }
        selectHTML += `</optgroup>`;
    });

    selectHTML += `</select><button type="button" class="remove-meal-btn" onclick="this.parentElement.remove()">-</button>`;
    newSelect.innerHTML = selectHTML;
    container.appendChild(newSelect);
}

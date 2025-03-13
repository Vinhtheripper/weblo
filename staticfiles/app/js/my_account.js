document.addEventListener("DOMContentLoaded", function () {
    // Kích hoạt tab menu
    let tabLinks = document.querySelectorAll('.account-settings-links a');
    tabLinks.forEach(function (tab) {
        tab.addEventListener("click", function (e) {
            e.preventDefault();
            document.querySelector('.account-settings-links .active').classList.remove("active");
            document.querySelector('.tab-pane.active').classList.remove("active", "show");
            this.classList.add("active");
            document.querySelector(this.getAttribute("href")).classList.add("active", "show");
        });
    });
    // Load lại dữ liệu đã lưu
    loadSavedMeals();
});

function saveMeals(day, mealType) {
    let username = document.getElementById("current-username").textContent; // Lấy username từ HTML
    if (!username) return; // Nếu không có username, không lưu

    let selects = document.querySelectorAll(`#meal-container-${day}-${mealType} select`);
    let selectedMeals = [];

    selects.forEach(select => {
        if (select.value) {
            selectedMeals.push(select.value);
        }
    });

    let mealPlanKey = `mealPlan_${username}`;
    let mealPlan = JSON.parse(localStorage.getItem(mealPlanKey)) || {};

    if (!mealPlan[day]) {
        mealPlan[day] = {};
    }
    mealPlan[day][mealType] = selectedMeals;
    localStorage.setItem(mealPlanKey, JSON.stringify(mealPlan));

    updateMealDisplay(day, mealType);
}
// Hiển thị danh sách món đã chọn
function updateMealDisplay(day, mealType) {
    let mealPlan = JSON.parse(localStorage.getItem("mealPlan")) || {};
    let selectedMeals = mealPlan[day] && mealPlan[day][mealType] ? mealPlan[day][mealType] : [];
    let displayElement = document.getElementById(`selected-meals-${day}-${mealType}`);
    displayElement.textContent = selectedMeals.length > 0 ? "Món đã chọn: " + selectedMeals.join(", ") : "Chưa có món";
}

// Load dữ liệu đã lưu sau khi refresh
function loadSavedMeals() {
    let username = document.getElementById("current-username").textContent;
    if (!username) return;

    let mealPlanKey = `mealPlan_${username}`;
    let mealPlan = JSON.parse(localStorage.getItem(mealPlanKey)) || {};

    for (let day in mealPlan) {
        for (let mealType in mealPlan[day]) {
            mealPlan[day][mealType].forEach(mealId => {
                addMealSelect(day, mealType, mealId);
            });
            updateMealDisplay(day, mealType);
        }
    }
}

// Thêm dropdown chọn món ăn
function addMealSelect(day, mealType, selectedValue = "") {
    let container = document.getElementById(`meal-container-${day}-${mealType}`);

    let newSelect = document.createElement("div");
    newSelect.classList.add("meal-select");

    let selectHTML = `<select name="meal_${day}_${mealType}" required><option value="">Chọn món</option>`;

    productCategories.forEach(category => {
        selectHTML += `<optgroup label="${category.name}">`;
        category.products.forEach(product => {
            selectHTML += `<option value="${product.id}" ${selectedValue == product.id ? "selected" : ""}>
                            ${product.name} (${product.calories} kcal)
                          </option>`;
        });
        selectHTML += `</optgroup>`;
    });

    selectHTML += `</select><button type="button" class="remove-meal-btn" onclick="this.parentElement.remove()">-</button>`;
    newSelect.innerHTML = selectHTML;
    container.appendChild(newSelect);
}

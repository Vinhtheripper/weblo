from django.shortcuts import render, redirect, get_object_or_404
from app.models import *
from django.contrib import messages


def my_account(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    products = Product.objects.all()
    orders = Order.objects.filter(customer=customer)
    product_categories = Category.objects.prefetch_related("products").all()

    if request.method == "POST":
        if "update_profile" in request.POST:
            update_profile(request, customer)

        if "track_weight" in request.POST:
            track_weight(request, customer)

        if "update_meal_plan" in request.POST:
            update_meal_plan(request, customer)

        return redirect("my_account")

    weight_logs = WeightTracking.objects.filter(customer=customer).order_by('-date')

    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meal_types = ["breakfast", "lunch", "dinner", "snacks"]
    context = {
        "customer": customer,
        'orders': orders,
        "meal_types": meal_types,
        "weight_logs": weight_logs,
        "week_days": week_days,
        "products": products,
        "product_categories": product_categories,
    }
    return render(request, "app/my_account.html", context)


def update_profile(request, customer):
    user = request.user
    user.username = request.POST.get("username", "").strip()
    user.email = request.POST.get("email", "").strip()

    full_name = request.POST.get("full_name", "").strip()
    name_parts = full_name.split(" ", 1)
    user.first_name = name_parts[0] if name_parts else ""
    user.last_name = name_parts[1] if len(name_parts) > 1 else ""

    user.save()

    if "customer_image" in request.FILES:
        customer.customer_image = request.FILES["customer_image"]
        customer.save()

    if "remove_photo" in request.POST:
        if customer.customer_image:
            customer.customer_image.delete(save=False)
        customer.customer_image = None
        customer.save()




def track_weight(request, customer):
    try:
        height = float(request.POST.get("height", 0))
        weight = float(request.POST.get("weight", 0))
        if height > 0 and weight > 0:
            bmi = round(weight / ((height / 100) ** 2), 2)

            # Xác định đánh giá sức khỏe dựa trên BMI
            if bmi < 18.5:
                health_status = "Underweight"
            elif 18.5 <= bmi < 24.9:
                health_status = "Normal"
            elif 25 <= bmi < 29.9:
                health_status = "Overweight"
            else:
                health_status = "Obesity"

            WeightTracking.objects.create(
                customer=customer,
                height=height,
                weight=weight,
                bmi=bmi,
                health_status=health_status
            )
            messages.success(request, f"Cập nhật cân nặng thành công! Đánh giá sức khỏe: {health_status}")
        else:
            messages.error(request, "Chiều cao và cân nặng phải lớn hơn 0!")
    except ValueError:
        messages.error(request, "Vui lòng nhập số hợp lệ cho chiều cao và cân nặng!")



def update_meal_plan(request, customer):
    print(request.POST)

    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        meal_plan, _ = MealPlan.objects.get_or_create(customer=customer, day=day)

        breakfast_items = request.POST.getlist(f"meal_{day}_breakfast")
        if breakfast_items:
            meal_plan.breakfast.set(breakfast_items)

        meal_plan.lunch.set(request.POST.getlist(f"meal_{day}_lunch"))
        meal_plan.dinner.set(request.POST.getlist(f"meal_{day}_dinner"))
        meal_plan.snacks.set(request.POST.getlist(f"meal_{day}_snacks"))
        meal_plan.save()

    order, _ = Order.objects.get_or_create(customer=customer, complete=False, defaults={"is_scheduled": True})
    order.is_scheduled = True
    order.save()
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        for meal_type in ["breakfast", "lunch", "dinner", "snacks"]:
            product_ids = request.POST.getlist(f"meal_{day}_{meal_type}")
            for product_id in product_ids:
                product = get_object_or_404(Product, id=product_id)
                order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
                if not created:
                    order_item.quantity += 1
                order_item.save()


    messages.success(request, "Cập nhật thực đơn thành công và thêm vào giỏ hàng!")

def meal_plan_view(request, customer):
    meal_plans = MealPlan.objects.filter(customer=customer).prefetch_related(
        "breakfast", "lunch", "dinner", "snacks"
    )

    meal_data = {}
    for meal in meal_plans:
        if meal.day not in meal_data:
            meal_data[meal.day] = {}

        for meal_type in ["breakfast", "lunch", "dinner", "snacks"]:
            if meal_type not in meal_data[meal.day]:
                meal_data[meal.day][meal_type] = set()

            meal_data[meal.day][meal_type].update(
                getattr(meal, meal_type).values_list("id", flat=True)
            )
    context = {
        "week_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "meal_types": ["breakfast", "lunch", "dinner", "snacks"],
        "product_categories": Category.objects.prefetch_related("products").all(),
        "meal_data": meal_data,
    }
    return render(request, "your_template.html", context)


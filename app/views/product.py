from django.shortcuts import render, get_object_or_404
from app.models import *

def menu(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items


        latest_tracking = WeightTracking.objects.filter(customer=customer, height__gte=100, weight__gte=10).order_by('-date', '-id').first()

        recommended_products = []

        if latest_tracking:
            bmi = latest_tracking.bmi
            print(f"User: {customer}, BMI: {bmi}")

            all_products = Product.objects.all()
            for p in all_products:
                print(f"Product: {p.name}, Calories: {p.calories}")


            if bmi < 18.5:
                recommended_products = Product.objects.filter(calories__gte=500)
            elif 18.5 <= bmi < 25:
                recommended_products = Product.objects.filter(calories__gte=300)
            elif 25 <= bmi < 30:
                recommended_products = Product.objects.filter(calories__lt=300)
            else:
                recommended_products = Product.objects.filter(calories__lt=200)

            print(f"Recommended products: {[p.name for p in recommended_products]}")
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        recommended_products = []

    categories = Category.objects.filter(is_sub=False)
    products_all = Product.objects.all()
    products = Product.objects.filter(digital=True)
    on_sale_products = Product.objects.filter(sale=True)
    combos = Combo.objects.all()
    new_products = Product.objects.filter(created_at__gte=datetime.now() - timedelta(days=7))

    context = {
        'products_all': products_all,
        'products': products,
        'on_sale_products': on_sale_products,
        'combos': combos,
        'user': request.user,
        'cartItems': cartItems,
        'categories': categories,
        'recommended_products': recommended_products,
        'new_products': new_products,
    }
    return render(request, 'app/menu.html', context)



def product_detail(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']

    categories = Category.objects.filter(is_sub=False)
    id = request.GET.get('id', '')
    products = Product.objects.filter(id=id) if id else Product.objects.none()
    products_all = Product.objects.all()


    product = products.first() if products.exists() else None
    is_on_sale = product.sale if product else False
    original_price = product.price if product else 0
    discounted_price = product.final_price if product else 0
    product_images = product.images.all() if product else []

    context = {
        'items': items,
        'order': order,
        'user': request.user,
        'cartItems': cartItems,
        'categories': categories,
        'products': products,
        'products_all': products_all,
        'is_on_sale': is_on_sale,
        'original_price': original_price,
        'discounted_price': discounted_price,
        'product_images': product_images,
    }
    return render(request, 'app/detail.html', context)



def combo_detail(request, id):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']

    combo = get_object_or_404(Combo, id=id)
    products_in_combo = combo.products.all()
    print(products_in_combo)

    # Tính tổng thành phần dinh dưỡng
    total_calories = sum(p.calories for p in products_in_combo)
    total_protein = sum(p.protein for p in products_in_combo)
    total_carbs = sum(p.carbs for p in products_in_combo)
    total_fat = sum(p.fat for p in products_in_combo)

    context = {
        'items': items,
        'order': order,
        'user': request.user,
        'cartItems': cartItems,
        'combo': combo,
        'products_in_combo': products_in_combo,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat,
        'combo_price': combo.get_combo_price,
    }
    return render(request, 'app/combo_detail.html', context)


def category(request):
    categories = Category.objects.filter(is_sub=False)[:5]
    active_category = request.GET.get('category', '')
    products = Product.objects.none()

    if active_category:
        products = Product.objects.filter(category__slug=active_category)

    context = {
        'categories': categories,
        'active_category': active_category,
        'products': products
    }
    return render(request, 'app/category.html', context)



def search(request):
    searched = ""
    products = Product.objects.none()

    if request.method == "POST":
        searched = request.POST.get("searched", "").strip()
        print(f"🔎 SEARCHED VALUE: {searched}")
        if searched:
            products = Product.objects.filter(name__icontains=searched)

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']


    on_sale_products = products.filter(sale=True)

    return render(request, 'app/search.html', {
        "searched": searched,
        "products": products,
        "on_sale_products": on_sale_products,
        "user": request.user,
        "cartItems": cartItems,
    })
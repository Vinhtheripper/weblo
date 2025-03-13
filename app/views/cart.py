from django.shortcuts import render, redirect, get_object_or_404
from app.models import *
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from decimal import Decimal

def cart(request):
    order = None  # Khởi tạo order ban đầu
    cartItems = 0
    cartTotal = Decimal('0.0')  # Chỉ khởi tạo một lần với Decimal

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total  # Đây đã là Decimal

        # Xử lý combo_items và product_items cho người dùng đã đăng nhập
        combo_items = [item for item in items if item.combo is not None]
        product_items = [item for item in items if item.product is not None]

    else:
        cart = request.session.get('cart', {})
        items = []

        for item_id, item_data in cart.items():
            if 'product_id' in item_data:
                product = Product.objects.get(id=item_data['product_id'])
                total_price = Decimal(str(product.price)) * item_data['quantity']  # Chuyển product.price thành Decimal
                items.append({'product': product, 'quantity': item_data['quantity'], 'total_price': total_price})
            elif 'combo_id' in item_data:
                combo = Combo.objects.get(id=item_data['combo_id'])
                total_price = combo.get_combo_price * item_data['quantity']  # combo.get_combo_price đã là Decimal
                items.append({'combo': combo, 'quantity': item_data['quantity'], 'total_price': total_price})

            cartItems += item_data['quantity']
            cartTotal += total_price  # Cộng dồn total_price (Decimal)

        request.session['cartItems'] = cartItems  # Cập nhật cartItems trong session

        # Xử lý combo_items và product_items cho khách vãng lai
        combo_items = [item for item in items if item.get('combo')]
        product_items = [item for item in items if item.get('product')]

    categories = Category.objects.filter(is_sub=False)
    context = {
        'combo_items': combo_items,
        'product_items': product_items,
        'cartItems': cartItems,
        'cartTotal': cartTotal,
        'categories': categories,
        'order': order  # Thêm order vào context
    }
    return render(request, 'app/cart.html', context)


def checkout(request):
    initial_data = {}
    order = None

    if request.user.is_authenticated:
        print("DEBUG - Người dùng đã đăng nhập.")
        try:
            customer = Customer.objects.get(user=request.user)
            print(f"DEBUG - Lấy Customer thành công: {customer}")

            order = Order.objects.filter(customer=customer, complete=False).first()
            if order:
                print(f"DEBUG - Lấy Order thành công: {order}")
            else:
                print("DEBUG - Không tìm thấy Order chưa hoàn thành.")

            if order:
                shipping_address = ShippingAddress.objects.filter(customer=customer).first()
                if shipping_address:
                    print(f"DEBUG - Lấy địa chỉ thành công: {shipping_address}")
                    initial_data = {
                        'address': shipping_address.address,
                        'city': shipping_address.city,
                        'state': shipping_address.state,
                        'mobile': shipping_address.mobile,
                    }
                else:
                    print("DEBUG - Không tìm thấy địa chỉ cho Order này.")
        except Exception as e:
            print(f"DEBUG - Lỗi khi lấy thông tin người dùng đã đăng nhập: {str(e)}")
    else:
        print("DEBUG - Người dùng chưa đăng nhập.")
        cart = request.session.get('cart', {})
        print(f"DEBUG - Giỏ hàng hiện tại: {cart}")

        if not cart:
            messages.error(request, "Giỏ hàng của bạn đang trống.")
            return redirect('cart')

        guest_order_id = request.session.get('guest_order_id')
        print(f"DEBUG - guest_order_id trong session: {guest_order_id}")

        if guest_order_id:
            guest_order = GuestOrder.objects.filter(id=guest_order_id).first()
            if guest_order:
                print(f"DEBUG - Lấy GuestOrder thành công: {guest_order}")
                order = guest_order.order
                shipping_address = ShippingAddress.objects.filter(order=order).first()

                if shipping_address:
                    print(f"DEBUG - Lấy địa chỉ thành công: {shipping_address}")
                    initial_data = {
                        'address': shipping_address.address,
                        'city': shipping_address.city,
                        'state': shipping_address.state,
                        'mobile': shipping_address.mobile,
                    }
                else:
                    print("DEBUG - Không tìm thấy địa chỉ cho Order của khách vãng lai.")
            else:
                print("DEBUG - Không tìm thấy GuestOrder với ID đã cung cấp.")
        else:
            print("DEBUG - Không có guest_order_id trong session. Tạo Order mới.")
            try:
                order = Order.objects.create(complete=False)
                for item_id, item_data in cart.items():
                    if 'product_id' in item_data:
                        product = Product.objects.get(id=item_data['product_id'])
                        OrderItem.objects.create(order=order, product=product, quantity=item_data['quantity'])
                        print(f"DEBUG - Thêm sản phẩm: {product} với số lượng {item_data['quantity']}")
                    elif 'combo_id' in item_data:
                        combo = Combo.objects.get(id=item_data['combo_id'])
                        OrderItem.objects.create(order=order, combo=combo, quantity=item_data['quantity'])
                        print(f"DEBUG - Thêm combo: {combo} với số lượng {item_data['quantity']}")

                guest_order = GuestOrder.objects.create(order=order)
                request.session['guest_order_id'] = guest_order.id
                print(f"DEBUG - Tạo GuestOrder thành công với ID: {guest_order.id}")
            except Exception as e:
                print(f"DEBUG - Lỗi khi tạo Order mới cho khách vãng lai: {str(e)}")

    if request.method == 'POST':
        guest_name = request.POST.get('guest_name', '').strip()
        guest_email = request.POST.get('guest_email', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        mobile = request.POST.get('mobile', '').strip()

        print("DEBUG - Dữ liệu POST nhận được:", {
            "guest_name": guest_name,
            "guest_email": guest_email,
            "address": address,
            "city": city,
            "state": state,
            "mobile": mobile
        })

        if not request.user.is_authenticated and (not guest_name or not guest_email):
            messages.error(request, "Vui lòng nhập đầy đủ tên và email.")
            return redirect('checkout')

        if not address or not city or not state or not mobile:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin địa chỉ.")
            return redirect('checkout')

        try:
            if not request.user.is_authenticated:
                guest_order.name = guest_name
                guest_order.email = guest_email
                guest_order.save()
                print("DEBUG - Lưu thông tin khách vãng lai thành công.")

            if request.user.is_authenticated:
                ShippingAddress.objects.update_or_create(
                    order=order,
                    customer=customer,
                    defaults={
                        'address': address,
                        'city': city,
                        'state': state,
                        'mobile': mobile,
                    }
                )
                print("DEBUG - Lưu địa chỉ thành công cho người dùng đã đăng nhập.")
            else:
                ShippingAddress.objects.update_or_create(
                    order=order,
                    defaults={
                        'address': address,
                        'city': city,
                        'state': state,
                        'mobile': mobile,
                    }
                )
                print("DEBUG - Lưu địa chỉ thành công cho khách vãng lai.")

            return redirect('payment')
        except Exception as e:
            print(f"DEBUG - Lỗi khi lưu địa chỉ: {str(e)}")

    if order:
        items = order.orderitem_set.all()
        print(f"DEBUG - Số lượng items trong Order: {len(items)}")
    else:
        items = []

    categories = Category.objects.filter(is_sub=False)
    context = {
        'categories': categories,
        'order': order,
        'items': items,
        'initial_data': initial_data,
    }
    print("DEBUG - Dữ liệu gửi về template:", context)

    return render(request, 'app/checkout.html', context)


def updateItem(request):
    if request.method == "POST":
        productId = request.POST.get("productId")
        comboId = request.POST.get("comboId")
        action = request.POST.get("action")

        if request.user.is_authenticated:
            customer, _ = Customer.objects.get_or_create(user=request.user)
            order, _ = Order.objects.get_or_create(customer=customer, complete=False)

            if productId:
                product = get_object_or_404(Product, id=productId)
                orderItem, _ = OrderItem.objects.get_or_create(order=order, product=product, combo=None)
            elif comboId:
                combo = get_object_or_404(Combo, id=comboId)
                orderItem, _ = OrderItem.objects.get_or_create(order=order, combo=combo, product=None)

            if action == "add":
                orderItem.quantity += 1
            if action == "remove":
                if orderItem.quantity > 1:
                    orderItem.quantity -= 1
                    orderItem.save()
                else:
                    print(f"Deleted item: {orderItem}")
                    orderItem.delete()

            elif action == "delete":
                orderItem.delete()

            if action != "delete":
                orderItem.save()

        else:
            cart = request.session.get('cart', {})

            if productId:
                if productId not in cart:
                    cart[productId] = {'product_id': int(productId), 'quantity': 0}
                if action == "add":
                    cart[productId]['quantity'] += 1
                if action == "remove":
                    if cart[productId]['quantity'] > 1:
                        cart[productId]['quantity'] -= 1
                    else:
                        del cart[productId]

                elif action == "delete":
                    del cart[productId]

            if comboId:
                if comboId not in cart:
                    cart[comboId] = {'combo_id': int(comboId), 'quantity': 0}
                if action == "add":
                    cart[comboId]['quantity'] += 1
                elif action == "remove":
                    cart[comboId]['quantity'] -= 1
                    if cart[comboId]['quantity'] <= 0:
                        del cart[comboId]
                elif action == "delete":
                    del cart[comboId]

            request.session['cart'] = cart
            total_items=sum(item['quantity'] for item in cart.values())
            request.session['cartItems']=total_items


        return redirect(request.META.get("HTTP_REFERER", "combo_list"))

    messages.error(request, "Yêu cầu không hợp lệ!")
    return redirect("cart")


def payment(request):
    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(user=request.user)
        order = Order.objects.filter(customer=customer, complete=False).first()
    else:
        guest_order_id = request.session.get('guest_order_id')
        if not guest_order_id:
            messages.warning(request, "Bạn chưa có đơn hàng nào.")
            return redirect('home')

        guest_order = GuestOrder.objects.get(id=guest_order_id)
        order = guest_order.order

    if not order:
        messages.warning(request, "Bạn chưa có đơn hàng nào.")
        return redirect('home')

    categories = Category.objects.filter(is_sub=False)
    context = {
        'order': order,
        'cartItems': order.get_cart_items,
        'categories': categories
    }
    return render(request, 'app/payment.html', context)


def confirm_payment(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)
            order = Order.objects.filter(customer=customer, complete=False).first()
        else:
            guest_order_id = request.session.get('guest_order_id')
            order = Order.objects.filter(guest_order__id=guest_order_id, complete=False).first() if guest_order_id else None

        if order:
            payment_method = request.POST.get('payment_method', '')
            order.complete = True
            order.transaction_id = "MANUAL_" + str(order.id)
            order.payment_method = payment_method
            order.save()

            if request.user.is_authenticated:
                total_items = sum(item.quantity for item in order.orderitem_set.all())
                points_earned = total_items // 5
                customer.points += points_earned
                customer.save()

                messages.success(request,
                                 f"Thanh toán thành công bằng {payment_method.upper()}! Bạn nhận được {points_earned} điểm thưởng.")
            else:
                messages.success(request,
                                 f"Thanh toán thành công bằng {payment_method.upper()}! Cảm ơn bạn đã mua hàng.")
                request.session.pop('guest_order_id', None)
                request.session.pop('cart', None)

            return redirect('payment_success')
        else:
            messages.warning(request, "Không tìm thấy đơn hàng cần thanh toán.")
            return redirect('cart')

    return redirect('payment')


def payment_success(request):
    return render(request, 'app/payment_success.html')

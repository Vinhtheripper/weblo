from django.shortcuts import render, redirect
from app.models import *
from django.contrib import messages

def home(request):
    return render(request, 'app/home.html')

def Contact(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname', '').strip() or "Anonymous"
        message_text = request.POST.get('message', '').strip()
        try:
            rating = int(request.POST.get('rating', 0))
            if rating < 1 or rating > 5:
                rating = 5
        except ValueError:
            rating = 5

        if request.user.is_authenticated:
            customer, created = Customer.objects.get_or_create(user=request.user)

            CustomerMessage.objects.create(
                customer=customer,
                nickname=nickname,
                message=message_text,
                rating=rating
            )

            messages.success(request, "Cảm ơn bạn đã chia sẻ câu chuyện!")
        else:
            messages.error(request, "Bạn cần đăng nhập để gửi message.")

        return redirect('contact')

    messages_list = CustomerMessage.objects.all().order_by('-created_at')
    return render(request, 'app/contact.html', {'messages_list': messages_list})

def Aboutus(request):
    return render(request, 'app/aboutus.html')

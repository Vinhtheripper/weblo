import ssl
from django.core.mail import EmailMessage
from django.utils.html import format_html
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os
from django.conf import settings
from email.mime.image import MIMEImage
from django.core.mail import get_connection
from .models import ShippingAddress


def truncate_text(text, max_length=30):
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def generate_invoice(order):
    """Tạo hóa đơn PDF theo mẫu chuẩn"""
    invoice_dir = os.path.join(settings.BASE_DIR, "invoices")
    os.makedirs(invoice_dir, exist_ok=True)
    pdf_path = os.path.join(invoice_dir, f"invoice_{order.id}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)

    c.drawCentredString(300, 770, "SALES INVOICE")
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "Store Name: DelisoraCompany")
    c.drawString(100, 730, "Address: 669 Do Muoi, Area 6, Thu Duc, Ho Chi Minh City")
    c.drawString(100, 710, "Phone Number: +84919694180")

    c.drawString(100, 680, f"Customer Name: {order.customer.user.get_full_name() if order.customer else 'Anonymous'}")

    shipping_address = ShippingAddress.objects.filter(customer=order.customer).order_by('-date_added').first()
    c.drawString(100, 660, f"Address: {shipping_address.address if shipping_address else 'N/A'}")

    # Tạo bảng dữ liệu
    data = [["NO", "NAME", "QUANTITY", "ORIGINAL PRICE", "SALE PRICE", "TOTAL AMOUNT"]]

    for i, item in enumerate(order.orderitem_set.all()):
        if item.product:
            item_name = truncate_text(item.product.name, max_length=30)
            original_price = item.product.price
            sale_price = f"{item.product.final_price} $" if item.product.sale else ""
        elif item.combo:
            item_name = truncate_text(item.combo.name, max_length=30)
            original_price = item.combo.get_combo_price
            sale_price = ""
        else:
            continue

        data.append([
            i + 1,
            item_name,
            item.quantity,
            f"{original_price} $",
            sale_price,
            f"{item.get_total} $"
        ])

    # Thêm hàng giảm giá
    data.append(["", "Sale Discount", "", "", "", f"- {order.get_sale_discount_total} $"])
    data.append(["", "Endow Discount", "", "", "", f"- {order.get_endow_discount_total} $"])

    # Vẽ bảng
    table = Table(data, colWidths=[50, 200, 80, 100, 100, 100])  # Tăng cột "NAME" lên 200px
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('WORDWRAP', (1, 1), (-1, -1)),  # Tự động xuống dòng nếu quá dài
    ]))

    table.wrapOn(c, 100, 400)
    table_width = sum([50, 200, 80, 100, 100, 100])  # Điều chỉnh width theo cột mới
    page_width = letter[0]
    table_x = (page_width - table_width) / 2
    table.drawOn(c, table_x, 500)

    # Tổng tiền
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(500, 460, f"TOTAL: {order.get_cart_total} $")

    c.drawString(100, 420, "CUSTOMER")
    c.drawString(400, 420, "VENDOR")

    c.save()
    return pdf_path


def send_invoice_email(customer_email, pdf_path, order):
    """Gửi email hóa đơn với logo hiển thị đúng"""
    logo_path = os.path.join(settings.BASE_DIR, "app/static/app/images/anhqq.png")

    subject = f"[Delisora] Confirm your order #{order.id}."
    message = format_html(
        """
        <div style="font-family: Arial, sans-serif; border: 1px solid #ddd; padding: 20px; max-width: 600px; text-align: center; margin: auto;">
            <div>
                <img src="cid:delisora_logo" alt="Delisora Logo" style="width: 150px;"/>
                <h2 style="color: #4CAF50; text-align: center;">Thanks for your order!</h2>
            </div>
            <p style="text-align: left;">Hello <strong>{}</strong>,</p>
            <p style="text-align: left;">Your order has been confirmed. A detailed invoice is attached.</p>
            <p style="text-align: left;">Thank you for trusting Delisora!</p>
            <p style="text-align: left;"><strong>Hotline:</strong> +84919694180</p>
        </div>
        """.format(order.customer.user.get_full_name() if order.customer else "Dear Customer")
    )

    connection = get_connection(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=True
    )
    connection.ssl_context.check_hostname = False
    connection.ssl_context.verify_mode = ssl.CERT_NONE

    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [customer_email], connection=connection)
    email.content_subtype = "html"


    if os.path.exists(logo_path):
        with open(logo_path, "rb") as img:
            logo = MIMEImage(img.read())
            logo.add_header("Content-ID", "<delisora_logo>")
            logo.add_header("Content-Disposition", "inline")
            logo.add_header("Content-Type", "image/png")
            email.attach(logo)


    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf:
            email.attach(f"invoice_{order.id}.pdf", pdf.read(), "application/pdf")

    email.send()

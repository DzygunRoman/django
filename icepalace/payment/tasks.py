from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order


@shared_task
def payment_completed(order_id):
    # отправка письма клиенту при успешной оплате
    order = Order.objects.get(id=order_id)
    subject = f' Ледовый дворец - Заказ № {order.id}'
    message = 'Пожалуйста, ознакомьтесь с чеком об оплате вашего заказа, он прикреплен к этому письму.'
    email = EmailMessage(subject,
                         message,
                         'dzygun-roman@mail.ru',
                         [order.email])
    # создание чека в формате pdf
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # прикрепление чека к письму и отправка письма
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    # отправить письмо
    email.send()

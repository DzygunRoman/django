from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
def order_created(order_id):
    # задание по отправке уведомления по электронной почте при успешном создании заказа
    order = Order.objects.get(id=order_id)
    subject = f'Заказ №. {order.id}'
    message = f'Дорогой {order.first_name},\n\n' \
            f'Вы успешно разместили заказ.' \
            f'Ваш заказ №. {order.id}.'
    mail_sent = send_mail(subject, message, 'dzygun-roman@mail.ru', [order.email])
    return mail_sent

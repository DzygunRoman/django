from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from orders.models import Order, OrderItem

#создаю экземпляр stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


@csrf_exempt
def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cansel_url = request.build_absolute_uri(reverse('payment:canceled'))
        #данные для создания платежа
        session_data = {'mode': 'payment',
                        'client_reference_id': order_id,
                        'success_url': success_url,
                        'cancel_url': cansel_url,
                        'line_items': []
                        }
        #добавляю услуги заказа в платеж
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency': 'rub',
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })
        #создаю сеанс оформления платежа
        session = stripe.checkout.Session.create(**session_data)
        #перенаправляю на страницу оплаты
        return redirect(session.url, code=303)
    else:
        return render(request, 'payment/process.html', locals())


def payment_completed(request):  # успешный платеж
    return render(request, 'payment/completed.html')


def payment_canceled(request):  # отмена платежа
    return render(request, 'payment/canceled.html')

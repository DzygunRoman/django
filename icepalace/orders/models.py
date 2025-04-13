from django.db import models
from django.conf import settings
from palace.models import Product


class Order(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Эл.почта')
    address = models.CharField(max_length=250, verbose_name='Адрес')
    postal_code = models.CharField(max_length=20, verbose_name='Индекс')
    city = models.CharField(max_length=100, verbose_name='Город')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    time_of_the_event = models.DateTimeField(verbose_name='Дата проведения мероприятия')
    paid = models.BooleanField(default=False, verbose_name='Оплачен')
    stripe_id = models.CharField(max_length=250, blank=True)#поле для хранения данных от stripe

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_stripe_url(self):
        if not self.stripe_id:
            # усли нет ассоциированых платежей
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            # путь stripe для иестовых платежей
            path = '/test/'
        else:
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)#on_delete=models.CASCADE если удалили заказ, то и заказы тоже удалються
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)#on_delete=models.CASCADE если удалили товар, то и заказы тоже удалються
    price = models.DecimalField(max_digits=10, decimal_places=2)#сколько цифр в числе и сколько цифр после запятой
    quantity = models.PositiveIntegerField(default=1)#сколько товаров добавили в заказ

    def __str__(self):#создаем строку с уникальным номером товара
        return str(self.id)

    def get_cost(self):#создаем функцию которая возвращает стоимость заказа
        return self.price * self.quantity

from decimal import Decimal
from django.conf import settings
from palace.models import Product


class Cart:  # класс корзины
    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)  # попытка получить корзину из сессии
        if not cart:
            # сохранить пустую корзину в сеансе
            cart = self.session[settings.CART_SESSION_ID] = {}  # создаем пустой словарь
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        product_id = str(product.id)  # получаем айди продукта
        if product_id not in self.cart:  # если продукта нет в корзине, то добавляем его
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """
        Обновление сессии cart
        """

        # пометить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, product):
        """
        Удаление товара из корзины.
        """
        product_id = str(product.id)  # получаем айди продукта
        if product_id in self.cart:  # если продукта нет в корзине, то добавляем его
            del self.cart[product_id]  # удаляем продукт
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)  # получаем продукты из базы данных
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())  # возвращаем количество товаров в корзине

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        return sum(Decimal(item['price']) * item['quantity']
                   for item in self.cart.values())

    def clear(self):
        """
        Удаление корзины из сессии.
        """
        del self.session[settings.CART_SESSION_ID]  # удаляем корзину из сессии
        self.save()

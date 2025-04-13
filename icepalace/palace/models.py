from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Категория')
    slug = models.CharField(max_length=200, unique=True, verbose_name='Слаг')

    class Meta:
        ordering = ['name']  # сортировка по имени
        indexes = [models.Index(fields=['name']), ]
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):# создание URL-адреса для категории
        return reverse('palace:product_list_by_category', args=[self.slug])


class Product(models.Model):
    # связь один ко многим - одна категория много товаров
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField(max_length=200, verbose_name='Услуга')
    # слаг этого товара для создания красивых URL-адресов
    slug = models.CharField(max_length=200, verbose_name='Слаг')
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name='Изображение')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    # наличие или отсутствие товара
    available = models.BooleanField(default=True, verbose_name='Доступен')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['id', 'slug']),
                   models.Index(fields=['name']),
                   models.Index(fields=['-created']),
                   ]
        verbose_name = 'услуга'
        verbose_name_plural = 'услуги'

    def __str__(self):# вывод названия товара
        return self.name

    def get_absolute_url(self):# создание URL-адреса для товара
        return reverse('palace:product_detail', args=[self.id, self.slug])


class Shedule(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название мероприятия')
    time_event = models.DateTimeField(verbose_name='Время мероприятия')
    slug = models.CharField(max_length=200, verbose_name='Слаг')

    class Meta:
        ordering = ['time_event']
        indexes = [models.Index(fields=['id', 'slug']),
                   models.Index(fields=['name']),
                   models.Index(fields=['-time_event']),
                   ]
        verbose_name = 'мероприятие'
        verbose_name_plural = 'мероприятия'

    def __str__(self):# вывод названия мероприятия
        return self.name

    def get_absolute_url(self):# создание URL-адреса для мероприятия
        return reverse('palace:shedule_detail', args=[self.id, self.slug])


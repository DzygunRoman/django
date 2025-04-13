import base64
import os
from collections import defaultdict
from django.urls import path
from django.shortcuts import render, redirect
from django.db.models import Sum, F
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from weasyprint import HTML
from django.conf import settings
from icepalace import settings
from .forms import DateRangeForm
from django.utils.html import format_html
import csv
import datetime
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem
from datetime import datetime
from xhtml2pdf import pisa
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from django.http import HttpResponseBadRequest
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.encoding import smart_str
import codecs



def export_to_csv(modeladmin, request, queryset):  # Функция для экспорта в csv
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response, delimiter=';')
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # записать заголовки в первую строку
    writer.writerow([field.verbose_name for field in fields])
    # записать данные в последующие строки
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d.%m.%Y %H:%M')
            data_row.append(str(value) if value is not None else '')
        writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Экспорт в  CSV'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


def order_stripe_payment(
        obj):  #Создаём функцию, которая будет выводить нам в админке ссылку на каждый объект Order c отображением списка
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ''


order_stripe_payment.short_description = 'Stripe payment'


def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">Просмотр</a>')


def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')


order_pdf.short_description = 'Invoice'


def _generate_report_data(start_date, end_date):  # Функция для генерации данных для отчета
    product_types = [
        {'name': 'Взрослый', 'key': 'adult'},
        {'name': 'Детский', 'key': 'child'},
        {'name': 'Зрительский', 'key': 'viewer'},
        {'name': 'Мужские', 'key': 'male_skates'},
        {'name': 'Женские', 'key': 'female_skates'},
    ]

    # Оптимизированный запрос
    items = OrderItem.objects.filter(
        order__time_of_the_event__range=(start_date, end_date),
        order__paid=True
    ).select_related('product').values(
        'order__time_of_the_event',
        'product__name'
    ).annotate(
        quantity=Sum('quantity'),
        total=Sum(F('price') * F('quantity'))
    ).order_by('order__time_of_the_event')

    # Обработка данных
    report = {
        'start_date': start_date,
        'end_date': end_date,
        'items': items,
        'product_types': product_types,
        'totals': {
            'quantity': sum(i['quantity'] for i in items),
            'amount': sum(i['total'] for i in items)
        }
    }

    return report


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'last_name', 'email',
        'address', 'postal_code', 'city',
        'created', 'updated', 'time_of_the_event', 'paid', order_detail, order_pdf]
    list_filter = ['paid', 'created', 'updated', 'time_of_the_event']
    search_fields = ['first_name', 'last_name', 'email']
    inlines = [OrderItemInline]
    actions = [export_to_csv]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sales-report/', self.admin_site.admin_view(self.sales_report), name='sales-report'),
            path('admin/sales-report/csv/', self.admin_site.admin_view(self.sales_report_csv), name='sales-report-csv'),
            path('sales-report/pdf/', self.admin_site.admin_view(self.sales_report_pdf), name='sales-report-pdf'),
            path('sales-report/csv/', self.admin_site.admin_view(self.sales_report_csv), name='sales-report-csv'),
        ]
        return custom_urls + urls

    change_list_template = 'admin/orders/order/change_list.html'  # Добавляем кастомный шаблон

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['report_url'] = reverse('admin:sales-report')  # URL для отчета
        return super().changelist_view(request, extra_context=extra_context)

    @staticmethod
    def get_report_data(start_date, end_date):
        product_types = [
            {'name': 'Взрослый', 'key': 'adult'},
            {'name': 'Детский', 'key': 'child'},
            {'name': 'Зрительский', 'key': 'viewer'},
            {'name': 'Мужские', 'key': 'male_skates'},
            {'name': 'Женские', 'key': 'female_skates'},
        ]

        # Правильный запрос к базе данных
        order_items = OrderItem.objects.filter(
            order__time_of_the_event__range=(start_date, end_date),
            order__paid=True,
            product__name__in=[pt['name'] for pt in product_types]
        ).values(
            'order__time_of_the_event',
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_sales=Sum(F('price') * F('quantity'))
        ).order_by('order__time_of_the_event')

        # Группировка данных
        grouped_data = defaultdict(lambda: {'quantities': defaultdict(int), 'total_sales': 0})
        for item in order_items:
            time = item['order__time_of_the_event']
            product = item['product__name']
            grouped_data[time]['quantities'][product] = item['total_quantity']
            grouped_data[time]['total_sales'] += item['total_sales']

        # Формирование таблицы
        table_data = []
        totals = {pt['key']: 0 for pt in product_types}
        totals['total_sales'] = 0

        for time in sorted(grouped_data.keys()):
            time_data = {'time': time}
            for pt in product_types:
                quantity = grouped_data[time]['quantities'].get(pt['name'], 0)
                time_data[pt['key']] = quantity
                totals[pt['key']] += quantity

            time_data['total_sales'] = grouped_data[time]['total_sales']
            totals['total_sales'] += grouped_data[time]['total_sales']
            table_data.append(time_data)

        return {
            'table_data': table_data,
            'product_types': product_types,
            'totals': totals,
            'start_date': start_date,
            'end_date': end_date
        }

    def _link_callback(self, uri, rel):
        """
        Callback для обработки ссылок в PDF
        """
        # Преобразование статических файлов
        if uri.startswith(settings.MEDIA_URL):
            path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
        elif uri.startswith(settings.STATIC_URL):
            path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
        else:
            # Для абсолютных URI
            return uri

        # Убедитесь, что файл существует
        if not os.path.isfile(path):
            raise Exception(f'media URI not found: {path}')
        return path

    def sales_report(self, request):
        form = DateRangeForm(request.POST or None)
        report_data = None  # Инициализируем переменную

        if request.method == 'POST' and form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Преобразуем в aware datetime
            start_datetime = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time()))
            end_datetime = timezone.make_aware(
                datetime.combine(end_date, datetime.max.time()))

            # Сохраняем в сессии
            request.session['report_start_date'] = start_datetime.isoformat()
            request.session['report_end_date'] = end_datetime.isoformat()

            # Перенаправляем на PDF или показываем данные
            if 'generate_pdf' in request.POST:
                return redirect('admin:sales-report-pdf')

            # Определение типов товаров
            product_types = [
                {'name': 'Взрослый', 'key': 'adult'},
                {'name': 'Детский', 'key': 'child'},
                {'name': 'Зрительский', 'key': 'viewer'},
                {'name': 'Мужские', 'key': 'male_skates'},
                {'name': 'Женские', 'key': 'female_skates'},
            ]
            product_names = [pt['name'] for pt in product_types]

            # Запрос данных
            order_items = OrderItem.objects.filter(
                order__time_of_the_event__gte=start_date,
                order__time_of_the_event__lte=end_date,
                order__paid=True,
                product__name__in=product_names
            ).values(
                'order__time_of_the_event', 'product__name'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_sales=Sum(F('price') * F('quantity'))
            ).order_by('order__time_of_the_event')

            # Группировка данных
            grouped_data = defaultdict(lambda: {'quantities': defaultdict(int), 'total_sales': 0})
            for item in order_items:
                time = item['order__time_of_the_event']
                product = item['product__name']
                grouped_data[time]['quantities'][product] = item['total_quantity']
                grouped_data[time]['total_sales'] += item['total_sales']

            # Формирование таблицы
            table_data = []
            totals = {pt['key']: 0 for pt in product_types}
            totals['total_sales'] = 0

            for time in sorted(grouped_data.keys()):
                time_data = {'time': time}
                for pt in product_types:
                    quantity = grouped_data[time]['quantities'].get(pt['name'], 0)
                    time_data[pt['key']] = quantity
                    totals[pt['key']] += quantity

                time_data['total_sales'] = grouped_data[time]['total_sales']
                totals['total_sales'] += grouped_data[time]['total_sales']
                table_data.append(time_data)

            report_data = {
                'table_data': table_data,
                'product_types': product_types,
                'totals': totals
            }

        context = self.admin_site.each_context(request)
        context.update({
            'form': form,
            'report_data': report_data,
            'has_dates': 'report_start_date' in request.session
        })
        return render(request, 'admin/sales_report.html', context)

    def sales_report_pdf(self, request):
        # Проверяем доступ к отчету
        if not request.user.has_perm('orders.view_order'):
            return HttpResponseForbidden("Доступ запрещен")

        # Получаем даты из сессии
        try:
            start_date = request.session.get('report_start_date')
            end_date = request.session.get('report_end_date')

            if not start_date or not end_date:
                return HttpResponseBadRequest("Необходимо сначала сформировать отчет")

            # Преобразуем строки в datetime
            start_date = timezone.datetime.fromisoformat(start_date)
            end_date = timezone.datetime.fromisoformat(end_date)

        except Exception as e:
            return HttpResponseBadRequest(f"Ошибка формата дат: {str(e)}")

        # Генерация PDF
        try:
            # Получаем данные
            report_data = self.get_report_data(start_date, end_date)

            # Контекст для шаблона
            context = {
                'report_data': report_data,
                'static_path': os.path.join(settings.BASE_DIR, 'static')
            }

            # Рендерим HTML
            html_string = render_to_string('admin/sales_report_pdf.html', context)

            # Создаем PDF документ
            html = HTML(
                string=html_string,
                base_url=request.build_absolute_uri('/')
            )

            # Генерируем PDF
            pdf = html.write_pdf()

            # Формируем HTTP ответ
            response = HttpResponse(
                pdf,
                content_type='application/pdf'
            )
            filename = f"sales_report_{start_date.date()}_{end_date.date()}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            return HttpResponseBadRequest(f"Ошибка генерации отчета: {str(e)}")

    def sales_report_csv(self, request):
        # Проверяем, есть ли даты в сессии
        if 'report_start_date' not in request.session:
            return HttpResponse("No report data available", status=400)

            # Получаем данные из сессии
        start_date = datetime.fromisoformat(request.session['report_start_date'])
        end_date = datetime.fromisoformat(request.session['report_end_date'])

        # Определение типов товаров (как в основном методе)
        product_types = [
            {'name': 'Взрослый', 'key': 'adult'},
            {'name': 'Детский', 'key': 'child'},
            {'name': 'Зрительский', 'key': 'viewer'},
            {'name': 'Мужские', 'key': 'male_skates'},
            {'name': 'Женские', 'key': 'female_skates'},
        ]

        # Получаем данные (аналогично основному методу)
        order_items = OrderItem.objects.filter(
            order__time_of_the_event__gte=start_date,
            order__time_of_the_event__lte=end_date,
            order__paid=True,
            product__name__in=[pt['name'] for pt in product_types]
        ).values(
            'order__time_of_the_event', 'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_sales=Sum(F('price') * F('quantity'))
        ).order_by('order__time_of_the_event')

        # Группируем данные (аналогично основному методу)
        grouped_data = defaultdict(lambda: {'quantities': defaultdict(int), 'total_sales': 0})
        for item in order_items:
            time = item['order__time_of_the_event']
            product = item['product__name']
            grouped_data[time]['quantities'][product] = item['total_quantity']
            grouped_data[time]['total_sales'] += item['total_sales']

        # Формируем таблицу (аналогично основному методу)
        table_data = []
        totals = {pt['key']: 0 for pt in product_types}
        totals['total_sales'] = 0

        for time in sorted(grouped_data.keys()):
            time_data = {'time': time}
            for pt in product_types:
                quantity = grouped_data[time]['quantities'].get(pt['name'], 0)
                time_data[pt['key']] = quantity
                totals[pt['key']] += quantity

            time_data['total_sales'] = grouped_data[time]['total_sales']
            totals['total_sales'] += grouped_data[time]['total_sales']
            table_data.append(time_data)

            # Создаем HTTP response с CSV и правильной кодировкой
            response = HttpResponse(
                content_type='text/csv; charset=utf-8-sig'  # utf-8-sig для Excel
            )
            response['Content-Disposition'] = 'attachment; filename="sales_report_{}.csv"'.format(
                datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            )

            # Пишем BOM для корректного открытия в Excel
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response, delimiter=';')  # Используем ; как разделитель

            # Заголовки столбцов
            headers = ['Время сеанса'] + [pt['name'] for pt in product_types] + ['Общая сумма']
            writer.writerow([smart_str(header) for header in headers])

            # Данные
            for row in table_data:
                csv_row = [row['time'].strftime("%Y-%m-%d %H:%M")]
                for pt in product_types:
                    csv_row.append(row[pt['key']])
                csv_row.append(row['total_sales'])
                writer.writerow([smart_str(str(item)) for item in csv_row])  # Явное преобразование в str

            # Итоговая строка
            totals_row = ['Итого:'] + [totals[pt['key']] for pt in product_types] + [totals['total_sales']]
            writer.writerow([smart_str(str(item)) for item in totals_row])

            return response
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Category, Product
from cart.forms import CartAddProductForm
from django.shortcuts import render
from .models import Shedule
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request,
                  'palace/product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products})


def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm()
    return render(request,
                  'palace/product/detail.html',
                  {'product': product, 'cart_product_form': cart_product_form})


def shedule_detail(request, id, slug):
    event = get_object_or_404(Shedule, id=id, slug=slug)
    return render(request, 'palace/shedule_detail.html', {'event': event})

def shedule_list(request):
    date_filter = request.GET.get('date')

    queryset = Shedule.objects.all()

    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d:%H:%M').date()
            queryset = queryset.filter(
                Q(time_event__date=filter_date) |
                Q(time_event__date__gt=filter_date)
            )
        except ValueError:
            pass

    queryset = queryset.order_by('time_event')
    # Получаем все мероприятия, отсортированные по времени
    all_events = Shedule.objects.all().order_by('time_event')

    # Пагинация - по 10 мероприятий на страницу
    paginator = Paginator(all_events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'current_date': timezone.now().date()  # Текущая дата для сравнения
    }
    return render(request, 'palace/shedule_list.html', context)


def home(request):
    categories = Category.objects.all()
    return render(request, 'palace/home.html', {'categories': categories})#

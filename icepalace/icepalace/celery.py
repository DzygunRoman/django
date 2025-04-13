import os

from celery import Celery

# задать стандартный модуль настроек Django
# для приложения 'celery'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icepalace.settings')#задется переменная для встроенной в Celery  программы командной строки
app = Celery('icepalace')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()# автоматически найдет задачи в файле tasks.py каждого приложения
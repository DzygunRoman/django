#импортировать celery
from .celery import app as celery_app

__all__ = ['celery_app']#добавил очередь заданий Celery  в проект и теперь можно запускать задачи
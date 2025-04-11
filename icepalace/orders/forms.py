from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'time_of_the_event']
        widgets = {
            'time_of_the_event': forms.DateTimeInput(attrs={
                'placeholder': 'дд.мм.гггг чч:мм',  # Заполнитель
                'type': 'datetime-local',  # HTML5 элемент для ввода даты и времени
                'class': 'form-control',  # CSS класс (опционально)
            }),
        }
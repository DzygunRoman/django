from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Order
from palace.models import Shedule


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Конечная дата должна быть после начальной")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Заполняем начальные значения из GET параметров
        if 'start_date' in self.data:
            self.fields['start_date'].initial = self.data['start_date']
        if 'end_date' in self.data:
            self.fields['end_date'].initial = self.data['end_date']


class OrderCreateForm(forms.ModelForm):


    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city',
                  'time_of_the_event']
        widgets = {
            'time_of_the_event': forms.DateTimeInput(attrs={
                'placeholder': 'дд.мм.гггг чч:мм',  # Заполнитель
                'type': 'datetime-local',  # HTML5 элемент для ввода даты и времени
                'class': 'form-control',  # CSS класс (опционально)
            }),
        }

    def clean_time_of_the_event(self):
        time_of_event = self.cleaned_data['time_of_the_event']

        # Проверяем, есть ли мероприятие с такой датой в расписании
        if not Shedule.objects.filter(time_event=time_of_event).exists():
            # Получаем ближайшие доступные даты
            nearest_events = Shedule.objects.filter(
                time_event__gte=timezone.now()
            ).order_by('time_event')[:3]

            error_message = "На указанное время нет мероприятий. "

            if nearest_events.exists():
                formatted_dates = [
                    e.time_event.strftime("%d.%m.%Y %H:%M")
                    for e in nearest_events
                ]
                error_message += f"Ближайшие доступные даты: {', '.join(formatted_dates)}"
            else:
                error_message += "Нет запланированных мероприятий."

            raise ValidationError(error_message)

        return time_of_event

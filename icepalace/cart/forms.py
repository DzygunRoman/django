from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):# форма для добавления товара в корзину
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int, label = 'Количество')  # Меняем название на русский
    override = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)
from django import forms
from .models import StockItem


class SaleForm(forms.Form):
    product_name = forms.CharField(label='Product Name', max_length=100)
    quantity = forms.IntegerField(label='Quantity')
    unit_price = forms.DecimalField(label='Unit Price', max_digits=10, decimal_places=2)
    total_price = forms.DecimalField(label='Total Price', max_digits=10, decimal_places=2)

    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        # Check if the quantity is valid
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive integer.")

        return cleaned_data


class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ['product_name', 'quantity', 'unit', 'price_per_unit']

from django.db import models, transaction
from django import forms
from datetime import datetime, timedelta

class StockItem(models.Model):
    ITEM_TYPES = (
        ('computer_accessory', 'Computer Accessory'),
        ('security_accessory', 'Security Accessory'),
    )
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=20)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES,default='computer_accessory')

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price_per_unit
        super(StockItem, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ['product_name', 'quantity', 'unit', 'price_per_unit']

class Sale(models.Model):
    product = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sale_date = models.DateTimeField(auto_now_add=True)
    company_name = models.CharField(max_length=100, default='Unknown Company')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super(Sale, self).save(*args, **kwargs)
            self.product.quantity -= self.quantity
            self.product.save()

class SalesReportImage(models.Model):
    image_data = models.BinaryField()

class SalesProduct(models.Model):
    company_name = models.CharField(max_length=100)
    days_valid = models.PositiveIntegerField(default=7)  # New field for days the quote is valid
    days_valid_unit = models.CharField(max_length=100,default='days')

    def __str__(self):
        return self.company_name

class SelectedProduct(models.Model):
    sales_product = models.ForeignKey(SalesProduct, on_delete=models.CASCADE)
    product = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def subtotal(self):
        return self.product.price_per_unit * self.quantity
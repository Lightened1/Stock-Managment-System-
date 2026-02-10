from django.shortcuts import render, redirect
from .forms import StockItemForm, SaleForm
from .models import StockItem,Sale,SalesReportImage
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import DatabaseError 
from django.http import JsonResponse
from django.template.loader import get_template





# Create your views here.
def home(request):
    return render(request, 'base.html')

def dashboard_view(request):
    stock_items = StockItem.objects.all()

    # Calculate total stock items
    total_stock_items = stock_items.count()

    # Calculate total price by summing prices of all stock items
    total_price = sum(item.total_price for item in stock_items)

    # Get list of products running out of stock (quantity < 5)
    low_stock_products = [item for item in stock_items if item.quantity < 5]

    return render(request, 'dashboard.html', {
        'total_stock_items': total_stock_items,
        'total_price': total_price,
        'low_stock_products': low_stock_products
    })

def stock_list_view(request):
    all_items = StockItem.objects.all()
    
    computer_accessories = StockItem.objects.filter(item_type='computer_accessory')
    security_accessories = StockItem.objects.filter(item_type='security_accessory')
    
    return render(request, 'stock_list.html', {'stock_items': all_items, 'computer_accessories': computer_accessories, 'security_accessories': security_accessories})
      
def add_stock_item(request):
    if request.method == 'POST':
        form = StockItemForm(request.POST)
        if form.is_valid():
            product_name = form.cleaned_data['product_name']
            quantity = form.cleaned_data['quantity']
            price_per_unit = form.cleaned_data['price_per_unit']

            existing_item = StockItem.objects.filter(product_name=product_name).first()

            if existing_item:
                existing_item.quantity += quantity
                existing_item.total_price = existing_item.quantity * existing_item.price_per_unit
                existing_item.save()
            else:
                new_item = form.save(commit=False)
                new_item.total_price = quantity * price_per_unit
                new_item.save()

            return redirect('stock_list')  # Redirect to the stock list page after adding/updating the item
        else:
            print(form.errors)  # Print form errors for debugging
    else:
        form = StockItemForm()

    return render(request, 'add_stock_item.html', {'form': form})

def fetch_stock_items(request):
    stock_items = StockItem.objects.all().values('total_price')
    return JsonResponse(list(stock_items), safe=False)



from decimal import Decimal
from django.shortcuts import render
from .models import StockItem

from decimal import Decimal
from django.shortcuts import render
from .models import StockItem, Sale

from django.shortcuts import render
from .models import StockItem, Sale, SalesProduct
from decimal import Decimal
from datetime import datetime, timedelta

def sell_product(request):
    products = StockItem.objects.all()
    selected_items = []
    total_price = Decimal('0')
    insufficient_items = []

    if request.method == 'POST':
        company_name = request.POST.get('company_name', '')  # Get company name from the form
        days_valid = int(request.POST.get('days_valid', 14))  # Get the validity period or default to 14 days
        days_valid_unit = request.POST.get('days_valid_unit','')
        sales_product = SalesProduct.objects.create(company_name=company_name, days_valid=days_valid, days_valid_unit=days_valid_unit)

        for product in products:
            quantity_key = f'quantity_{product.id}'
            quantity_str = request.POST.get(quantity_key, '')  # Get quantity as a string

            if quantity_str.isdigit():  # Check if quantity is a string containing only digits
                quantity = int(quantity_str)

                if quantity > 0 and quantity <= product.quantity:  # Check if requested quantity is positive and can be sold
                    product.quantity -= quantity
                    product.save()

                    # Update the quantity sold for the product
                    Sale.objects.create(product=product, quantity=quantity)

                    subtotal = quantity * product.price_per_unit
                    selected_items.append({
                        'product': product,
                        'quantity': quantity,
                        'subtotal': subtotal
                    })
                    total_price += subtotal
                elif quantity > 0 and quantity > product.quantity:  # Check if requested quantity exceeds available stock
                    insufficient_items.append(product)

        if insufficient_items:
            return render(request, 'insufficient_stock.html', {'insufficient_items': insufficient_items})

        if selected_items:
            vat = total_price * Decimal('0.15')
            total_price_incl_vat = total_price + vat

            expiration_date = datetime.now() + timedelta(days=days_valid)

            return render(request, 'sale_summary.html', {
                'company_name': company_name,
                'selected_items': selected_items,
                'total_price': total_price,
                'vat': vat,
                'total_price_incl_vat': total_price_incl_vat,
                'days_valid': days_valid,
                'days_valid_unit': days_valid_unit,
                'expiration_date': expiration_date
            })

    return render(request, 'sell_product.html', {'products': products})

import base64
def save_sales_summary_image(request):
    if request.method == 'POST':
        image_data = request.POST.get('image_data')
        
        # Decode the base64 image data
        _, imgstr = image_data.split(';base64,') 
        image_data = base64.b64decode(imgstr)

        # Save the image in the database
        sales_report_image = SalesReportImage(image_data=image_data)
        sales_report_image.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def delete_stock_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            stock_item = StockItem.objects.get(id=item_id)
            stock_item.delete()
            return JsonResponse({'success': True})
        except StockItem.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False}) 

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO  

def sales_graph_view(request):
    # Query your sales data
    sales_data = Sale.objects.all()

    # Extract relevant data for the graph (e.g., sales amounts)
    companies = [sale.company_name for sale in sales_data]
    sales_amounts = [sale.amount for sale in sales_data]

    # Create a bar chart
    plt.bar(companies, sales_amounts)
    plt.xlabel('Companies')
    plt.ylabel('Sales Amounts')
    plt.title('Sales Report')

    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode the image data in base64 for display in the template
    graphic = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'sales_graph.html', {'graphic': graphic})

from django.db.models import Sum
from datetime import datetime, timedelta

def sales_report(request):
    # Calculate the start and end dates for the current week
    today = datetime.now().date()
    start_week = today - timedelta(days=today.weekday())
    
    # Query sales data for the current week
    sales_data = Sale.objects.filter(sale_date__range=[start_week, today])

    # Aggregate sales data
    product_sales = sales_data.values('product__product_name').annotate(total_sold=Sum('quantity'))

    # Get all products
    all_products = StockItem.objects.all()

    context = {
        'product_sales': product_sales,
        'all_products': all_products,
    }

    return render(request, 'sales_report.html', context)


def batch_sale_view(request):
    stock_items = StockItem.objects.all()  
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        for item in stock_items:
            quantity = request.POST.get(f'quantity_{item.id}')
            if quantity:
                # Process the sale for each stock item
                Sale.objects.create(
                    product=item,
                    quantity=quantity,
                    company_name=company_name
                )
        # Redirect to the sales report page after processing the sale
        return HttpResponseRedirect('/sales_report/')  # Update the URL to the sales report page

    return render(request, 'batch_sale.html', {'stock_items': stock_items})

from django.db.models.functions import Coalesce
def sales_report_view(request):
    # Aggregate sales data to get the total quantity sold for each product
    product_sales = Sale.objects.values('product').annotate(total_sold=Sum('quantity')).order_by('-total_sold')

    # Retrieve all products from the StockItem model
    all_products = StockItem.objects.all()

    # Create a dictionary mapping product IDs to product names for easy lookup
    product_names = {product.id: product.product_name for product in all_products}

    # Include product names in the product_sales data
    for sale in product_sales:
        product_id = sale['product']
        sale['product_name'] = product_names.get(product_id, 'Unknown Product')

    # Find unsold products
    unsold_products = [product for product in all_products if product.id not in [sale['product'] for sale in product_sales]]

    # Determine the most sold product
    most_sold_product = None
    if product_sales:
        most_sold_product_id = product_sales[0]['product']
        most_sold_product = StockItem.objects.get(id=most_sold_product_id)

    return render(request, 'sales_report.html', {
        'product_sales': product_sales,
        'unsold_products': unsold_products,
        'most_sold_product': most_sold_product
    })
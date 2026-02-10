"""
URL configuration for stock_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from inventory.views import home,dashboard_view ,stock_list_view,add_stock_item,sales_report_view,sell_product,delete_stock_item,fetch_stock_items,save_sales_summary_image,sales_graph_view,batch_sale_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),  
    path('stock-list/', stock_list_view, name='stock_list'),
    path('add-stock-item/', add_stock_item, name='add_stock_item'), 
    path('sales-report/', sales_report_view, name='sales_report'),
    path('sell/', sell_product, name='sell_product'),
    path('delete-stock-item/', delete_stock_item, name='delete_stock_item'),
    path('fetch_stock_items/', fetch_stock_items, name='fetch_stock_items'),
    path('save-image/', save_sales_summary_image, name='save_sales_summary_image'),
    path('sales-graph/', sales_graph_view, name='sales_graph_view'),
    path('batch_sale/', batch_sale_view, name='batch_sale'),
    
]


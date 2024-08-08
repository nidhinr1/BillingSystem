from django.contrib import admin
from .models import Category,Billing,Product,stock,Sales
admin.site.register(Category)
admin.site.register(Billing)
admin.site.register(Product)
admin.site.register(stock)
admin.site.register(Sales)

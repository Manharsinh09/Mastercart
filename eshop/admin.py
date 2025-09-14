from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product,Categories,SubCategories,Order,OrderItem,Contact
# Register your models here.

class OrderItemTubinlines(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemTubinlines]

admin.site.register(Product)
admin.site.register(Categories)
admin.site.register(SubCategories)

admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Contact)
from django.contrib import admin
from .models import Product, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'average_rating')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'brand', 'description')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'rating', 'is_moderated', 'created_at')
    list_filter = ('is_moderated', 'rating', 'product__category', 'product__brand')
    search_fields = ('author__username', 'product__name', 'text')

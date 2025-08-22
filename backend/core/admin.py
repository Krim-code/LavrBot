from django.contrib import admin
from .models import Brand, Category, Product, ProductFile, Question


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "is_premium", "sort_order")
    list_filter = ("is_premium",)
    search_fields = ("name",)
    ordering = ("is_premium", "sort_order", "name")
    list_editable = ("sort_order",)  # вот это ключ — правим прямо из списка

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class ProductFileInline(admin.TabularInline):
    model = ProductFile
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('article', 'title', 'brand', 'category', 'is_published', 'created_at')
    list_filter = ('brand', 'category', 'is_published')
    search_fields = ('article', 'title', 'description')
    inlines = [ProductFileInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('contact', 'product', 'created_at')
    search_fields = ('contact', 'message')
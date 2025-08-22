from rest_framework import serializers
from .models import Brand, Category, Product, ProductFile, Question


# core/serializers.py
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "description", "is_premium", "archive", "sort_order"]



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFile
        fields = ['id', 'file', 'format', 'size_bytes']


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    category = CategorySerializer()
    files = ProductFileSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'article',
            'brand',
            'category',
            'description',
            'is_published',
            'created_at',
            'files'
        ]


class QuestionSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'contact',
            'message',
            'product',
            'created_at'
        ]

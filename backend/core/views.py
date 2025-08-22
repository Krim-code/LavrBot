from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Brand, Category, Product, Question
from django.db.models import QuerySet
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductSerializer,
    QuestionSerializer
)

def _apply_ordering(qs: QuerySet, request):
    ordering = request.query_params.get("ordering")
    allowed = {"name", "-name", "id", "-id", "sort_order", "-sort_order"}
    if ordering in allowed:
        return qs.order_by(ordering)
    # дефолт: ручной порядок, потом по имени
    return qs.order_by("sort_order", "name")

class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    @action(detail=False)
    def premium(self, request):
        qs = _apply_ordering(Brand.objects.filter(is_premium=True), request)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False)
    def regular(self, request):
        qs = _apply_ordering(Brand.objects.filter(is_premium=False), request)
        return Response(self.get_serializer(qs, many=True).data)
    
    @action(detail=True, methods=["get"])
    def categories(self, request, pk=None):
        brand = self.get_object()
        categories = Category.objects.filter(product__brand=brand).distinct()
        return Response(CategorySerializer(categories, many=True).data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        brand_id = self.request.query_params.get('brand_id')
        if brand_id:
            # Получаем категории, у которых есть товары от данного бренда
            return Category.objects.filter(product__brand_id=brand_id).distinct()
        return Category.objects.all()


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [filters.OrderingFilter,filters.SearchFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    search_fields = ['article']

    def get_queryset(self):
        qs = Product.objects.filter(is_published=True).prefetch_related('files', 'brand', 'category')

        brand_id = self.request.query_params.get('brand_id')
        category_id = self.request.query_params.get('category_id')

        if brand_id:
            qs = qs.filter(brand_id=brand_id)
        if category_id:
            qs = qs.filter(category_id=category_id)

        return qs


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    http_method_names = ['get', 'post']

from rest_framework.routers import DefaultRouter
from core.views import (
    BrandViewSet, CategoryViewSet,
    ProductViewSet, QuestionViewSet
)
from django.urls import path, include

router = DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'categories', CategoryViewSet,basename='categories')
router.register(r'products', ProductViewSet,basename='product')
router.register(r'questions', QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

from django.db import models


# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_premium = models.BooleanField(default=False)
    archive = models.FileField(upload_to='brands/zips/', blank=True, null=True)

    # ручной порядок
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("sort_order", "name")  # дефолтная сортировка везде
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    article = models.CharField(max_length=100, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.article} — {self.title}"


class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='products/files/')
    format = models.CharField(max_length=20)  # e.g. STL, OBJ, ZIP
    size_bytes = models.IntegerField()

    def __str__(self):
        return f"{self.product.article} [{self.format}]"


class Question(models.Model):
    contact = models.CharField(max_length=255)  # telegram id/email/имя
    message = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question from {self.contact} at {self.created_at}"

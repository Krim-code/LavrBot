import random
import io
import zipfile

from django.core.files.base import ContentFile
from .models import Brand, Category, Product, ProductFile

def generate():
    ProductFile.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Brand.objects.all().delete()

    # Бренды
    brands_data = [
        ("Boyard", "Boyard - описание бренда", True),
        ("Hettich", "Hettich - описание бренда", True),
        ("LaurusPro", "LaurusPro - описание бренда", True),
        ("GTV", "GTV - описание бренда", False),
        ("Blum", "Blum - описание бренда", False),
    ]

    brands = {}
    for name, description, is_premium in brands_data:
        brand = Brand.objects.create(name=name, description=description, is_premium=is_premium)
        brands[name] = brand

    # Категории
    category_objs = []
    for name in ["Ручки", "Петли", "Направляющие", "Крючки", "Опоры"]:
        category_objs.append(Category.objects.create(name=name))

    # Продукты и файлы
    for i in range(1, 100):
        brand = random.choice(list(brands.values()))
        category = random.choice(category_objs)

        product = Product.objects.create(
            title=f"Фурнитура {i}",
            article=f"ART{i:04d}",
            brand=brand,
            category=category,
            description=f"Описание товара {i}"
        )

        content = f"Fake file content {i}".encode()
        ProductFile.objects.create(
            product=product,
            format="txt",
            size_bytes=len(content),
            file=ContentFile(content, name=f"model_{i}.txt")
        )

    # Генерация архивов по брендам
    for brand in Brand.objects.all():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zipf:
            files = ProductFile.objects.filter(product__brand=brand)
            for pf in files:
                pf.file.open()
                zipf.writestr(pf.file.name.split("/")[-1], pf.file.read())
                pf.file.close()

        buffer.seek(0)
        brand.archive.save(f"{brand.name.lower()}_archive.zip", ContentFile(buffer.read()))
        buffer.close()

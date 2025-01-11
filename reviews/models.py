from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название товара")
    CATEGORY_CHOICES = [
        ('cosmetics', 'Косметика'),
        ('clothing', 'Одежда'),
        ('accessories', 'Аксессуары'),
        ('skincare', 'Уход за кожей'),
        ('haircare', 'Уход за волосами'),
        ('footwear', 'Обувь'),
    ]
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name="Категория"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Картинка")
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name="Бренд")

    def delete(self, *args, **kwargs):
        Review.objects.filter(product=self).delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        avg_rating = self.reviews.aggregate(Avg('rating')).get('rating__avg')
        return round(avg_rating, 2) if avg_rating is not None else "Нет отзывов"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Товар"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name="Оценка"
    )
    is_moderated = models.BooleanField(
        default=False,
        verbose_name="Проверен"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата редактирования"
    )

    def save(self, *args, **kwargs):
        if not self.is_moderated:
            self.is_moderated = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Отзыв от {self.author} на {self.product}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

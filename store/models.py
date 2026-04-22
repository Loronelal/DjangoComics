from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import unique_slugify

class Category(models.Model):
    """Категория комиксов"""
    name = models.CharField('Название категории', max_length=100)
    slug = models.SlugField('URL', unique=True, max_length=100)
    description = models.TextField('Описание категории', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])


class Publisher(models.Model):
    """Издательство"""
    name = models.CharField('Название издательства', max_length=100)
    slug = models.SlugField('URL', unique=True, max_length=100)
    country = models.CharField('Страна', max_length=100)
    website = models.URLField('Сайт', blank=True)
    founded_year = models.IntegerField('Год основания', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Comic(models.Model):
    """Модель комикса"""
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', unique=True, max_length=200)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='comics'
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        verbose_name='Издательство',
        related_name='comics'
    )
    author = models.CharField('Автор/Художник', max_length=200)
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.IntegerField(
        'Количество в наличии',
        default=0,
        validators=[MinValueValidator(0)]
    )
    rating = models.FloatField(
        'Рейтинг',
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    release_date = models.DateField('Дата выпуска')
    pages = models.IntegerField('Количество страниц')
    language = models.CharField('Язык', max_length=50, default='Русский')
    description = models.TextField('Описание')
    cover_image = models.ImageField(
        'Обложка',
        upload_to='comics/',
        blank=True,
        null=True
    )

    image_url = models.URLField(
        'Ссылка на изображение',
        max_length=500,
        blank=True,
        null=True,
        help_text='Вставьте ссылку на картинку (будет использоваться вместо загруженного файла)'
    )

    preview_pages = models.JSONField(
    'Страницы отрывка',
    default=list,
    blank=True,
    help_text='Список URL изображений страниц в формате JSON, например ["https://...", "..."]'
    )

    is_bestseller = models.BooleanField('Бестселлер', default=False)
    is_new = models.BooleanField('Новинка', default=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Комикс'
        verbose_name_plural = 'Комиксы'
        ordering = ['-created_at', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.publisher.name})"
    
    def get_absolute_url(self):
        return reverse('comic_detail', args=[self.slug])
    
    @property
    def is_available(self):
        return self.stock > 0


class Favorite(models.Model):
    """Избранное (для интерактивного элемента)"""
    comic = models.ForeignKey(
        Comic,
        on_delete=models.CASCADE,
        verbose_name='Комикс',
        related_name='favorites'
    )
    session_key = models.CharField('Ключ сессии', max_length=40)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['comic', 'session_key']
    
    def __str__(self):
        return f"{self.comic.title} в избранном"
    

class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.session_key}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.comic.price * self.quantity
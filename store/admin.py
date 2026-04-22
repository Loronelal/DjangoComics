from django.contrib import admin
from .models import Category, Publisher, Comic, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'founded_year']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'country']


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'publisher', 'price', 'stock', 
        'rating', 'is_bestseller', 'is_new', 'is_available', 'image_url'
    ]
    list_filter = ['category', 'publisher', 'language', 'is_bestseller', 'is_new']
    search_fields = ['title', 'author', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['price', 'stock', 'rating', 'is_bestseller', 'is_new']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'category', 'publisher', 'author', 'description')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'stock')
        }),
        ('Характеристики', {
            'fields': ('rating', 'release_date', 'pages', 'language')
        }),
        ('Статус', {
            'fields': ('is_bestseller', 'is_new')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Изображение', {
            'fields': ('cover_image', 'image_url')
        }),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['comic', 'session_key', 'created_at']
    list_filter = ['created_at']
# store/utils.py
from transliterate import translit
import re

def unique_slugify(instance, title, slug_field='slug'):
    """
    Генерирует уникальный слаг на основе title с транслитерацией русских символов.
    """
    # Транслитерация кириллицы в латиницу
    slug = translit(title, 'ru', reversed=True)
    # Оставляем только буквы, цифры, пробелы и дефисы
    slug = re.sub(r'[^\w\s-]', '', slug).strip().lower()
    # Заменяем пробелы и подчёркивания на дефисы
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Убираем дефисы в начале и конце
    slug = slug.strip('-')
    
    # Если после очистки ничего не осталось, используем запасной вариант
    if not slug:
        slug = f"comic-{instance.pk or 'new'}"
    
    # Проверка уникальности
    Klass = instance.__class__
    original_slug = slug
    counter = 1
    while Klass.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{original_slug}-{counter}"
        counter += 1
    
    return slug
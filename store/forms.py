from django import forms
from .models import Comic, Category, Publisher
from django.core.exceptions import ValidationError

class ComicForm(forms.ModelForm):
    class Meta:
        model = Comic
        fields = [
            'title', 'category', 'publisher', 'author', 'price', 
            'stock', 'rating', 'release_date', 'pages', 'language', 
            'description', 'cover_image', 'is_bestseller', 'is_new'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'publisher': forms.Select(attrs={'class': 'form-select'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pages': forms.NumberInput(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/image.jpg'}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise ValidationError('Цена не может быть отрицательной')
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock and stock < 0:
            raise ValidationError('Количество не может быть отрицательным')
        return stock
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 0 or rating > 5):
            raise ValidationError('Рейтинг должен быть от 0 до 5')
        return rating


class ComicFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        label='Издательство',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_price = forms.DecimalField(
        required=False,
        label='Мин. цена',
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    max_price = forms.DecimalField(
        required=False,
        label='Макс. цена',
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    in_stock = forms.BooleanField(
        required=False,
        label='Только в наличии',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
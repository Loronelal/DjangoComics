from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from django.utils.text import slugify
from .models import Comic, Category, Publisher, Favorite
from .forms import ComicForm, ComicFilterForm
from .utils import unique_slugify

class IndexView(ListView):
    """Главная страница"""
    model = Comic
    template_name = 'index.html'
    context_object_name = 'comics'
    
    def get_queryset(self):
        return Comic.objects.filter(is_bestseller=True)[:6]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_comics'] = Comic.objects.filter(is_new=True)[:6]
        context['categories'] = Category.objects.all()
        return context


class ComicListView(ListView):
    """Список комиксов"""
    model = Comic
    template_name = 'comic_list.html'
    context_object_name = 'comics'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Comic.objects.all()
        
        # Фильтрация по параметрам
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        publisher_slug = self.request.GET.get('publisher')
        if publisher_slug:
            queryset = queryset.filter(publisher__slug=publisher_slug)
        
        min_price = self.request.GET.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.GET.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        in_stock = self.request.GET.get('in_stock')
        if in_stock == 'on':
            queryset = queryset.filter(stock__gt=0)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ComicFilterForm(self.request.GET)
        context['categories'] = Category.objects.all()
        context['publishers'] = Publisher.objects.all()
        return context


class ComicDetailView(DetailView):
    """Детальная информация о комиксе"""
    model = Comic
    template_name = 'comic_detail.html'
    context_object_name = 'comic'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        
        context['is_favorite'] = Favorite.objects.filter(
            comic=self.object,
            session_key=session_key
        ).exists()
        return context


class ComicCreateView(CreateView):
    """Создание комикса"""
    model = Comic
    form_class = ComicForm
    template_name = 'comic_form.html'
    success_url = reverse_lazy('store:comic_list')   # ← исправлено
    
    def form_valid(self, form):
        if not form.instance.slug:
            form.instance.slug = unique_slugify(form.instance, form.instance.title)
        messages.success(self.request, 'Комикс успешно добавлен!')
        return super().form_valid(form)
    
    
    def form_invalid(self, form):
        messages.error(self.request, 'Исправьте ошибки в форме.')
        return super().form_invalid(form)


class ComicUpdateView(UpdateView):
    """Редактирование комикса"""
    model = Comic
    form_class = ComicForm
    template_name = 'comic_form.html'
    success_url = reverse_lazy('store:comic_list')   # ← исправлено
    
    def form_valid(self, form):
        if not form.instance.slug:
            form.instance.slug = unique_slugify(form.instance, form.instance.title)
        messages.success(self.request, 'Комикс успешно обновлен!')
        return super().form_valid(form) 
    
    def form_invalid(self, form):
        messages.error(self.request, 'Исправьте ошибки в форме.')
        return super().form_invalid(form)


class ComicDeleteView(DeleteView):
    """Удаление комикса"""
    model = Comic
    template_name = 'comic_confirm_delete.html'
    success_url = reverse_lazy('store:comic_list')   # ← исправлено
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Комикс успешно удален!')
        return super().delete(request, *args, **kwargs)


def comic_filter_ajax(request):
    """AJAX фильтрация комиксов"""
    queryset = Comic.objects.all()
    
    # Фильтрация
    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category__slug=category)
    
    publisher = request.GET.get('publisher')
    if publisher:
        queryset = queryset.filter(publisher__slug=publisher)
    
    min_price = request.GET.get('min_price')
    if min_price:
        queryset = queryset.filter(price__gte=float(min_price))
    
    max_price = request.GET.get('max_price')
    if max_price:
        queryset = queryset.filter(price__lte=float(max_price))
    
    in_stock = request.GET.get('in_stock')
    if in_stock == 'true':
        queryset = queryset.filter(stock__gt=0)
    
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search)
        )
    
    # Пагинация
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 12)
    
    try:
        comics = paginator.page(page)
    except PageNotAnInteger:
        comics = paginator.page(1)
    except EmptyPage:
        comics = paginator.page(paginator.num_pages)
    
    # Формируем HTML для ответа
    from django.template.loader import render_to_string
    html = render_to_string('partials/comic_list_items.html', {'comics': comics})
    
    return JsonResponse({
        'html': html,
        'has_next': comics.has_next(),
        'page': comics.number,
        'total': paginator.count
    })


@require_http_methods(["POST"])
def toggle_favorite(request):
    """Добавление/удаление из избранного"""
    try:
        data = json.loads(request.body)
        comic_id = data.get('comic_id')
        
        if not comic_id:
            return JsonResponse({'error': 'ID комикса не указан'}, status=400)
        
        comic = get_object_or_404(Comic, id=comic_id)
        
        # Получаем или создаем сессию
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        favorite, created = Favorite.objects.get_or_create(
            comic=comic,
            session_key=session_key
        )
        
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
        
        favorites_count = Favorite.objects.filter(session_key=session_key).count()
        
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'favorites_count': favorites_count
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def quick_view(request, pk):
    """Быстрый просмотр комикса в модальном окне"""
    comic = get_object_or_404(Comic, pk=pk)
    from django.template.loader import render_to_string
    html = render_to_string('partials/comic_quick_view.html', {'comic': comic})
    return JsonResponse({'html': html})


from .models import Cart, CartItem

def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def cart_add(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, comic=comic)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_items = sum(item.quantity for item in cart.items.all())
        return JsonResponse({
            'success': True,
            'message': f'"{comic.title}" добавлен в корзину',
            'cart_count': total_items
        })
    else:
        messages.success(request, f'"{comic.title}" добавлен в корзину')
        return redirect(request.META.get('HTTP_REFERER', 'comic_list'))

def cart_remove(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    cart = get_or_create_cart(request)
    CartItem.objects.filter(cart=cart, comic=comic).delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        total_items = sum(item.quantity for item in cart.items.all())
        return JsonResponse({
            'success': True,
            'message': f'"{comic.title}" удалён из корзины',
            'cart_count': total_items
        })
    else:
        messages.success(request, f'"{comic.title}" удалён из корзины')
        return redirect(request.META.get('HTTP_REFERER', 'comic_list'))

def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart_detail.html', {'cart': cart})

def favorites_count(request):
    """Возвращает количество избранных комиксов для текущей сессии"""
    if not request.session.session_key:
        request.session.create()
    count = Favorite.objects.filter(session_key=request.session.session_key).count()
    return JsonResponse({'count': count})

def cart_count(request):
    """Возвращает количество товаров в корзине для текущей сессии"""
    if not request.session.session_key:
        request.session.create()
    cart = get_or_create_cart(request)
    total_items = sum(item.quantity for item in cart.items.all())
    return JsonResponse({'count': total_items})


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class ComicListView(ListView):
    model = Comic
    template_name = 'comic_list.html'
    context_object_name = 'comics'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Явная пагинация (на случай, если стандартная не сработала)
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page', 1)
        try:
            comics = paginator.page(page)
        except PageNotAnInteger:
            comics = paginator.page(1)
        except EmptyPage:
            comics = paginator.page(paginator.num_pages)

        context['comics'] = comics
        context['filter_form'] = ComicFilterForm(self.request.GET)
        context['categories'] = Category.objects.all()
        context['publishers'] = Publisher.objects.all()
        return context
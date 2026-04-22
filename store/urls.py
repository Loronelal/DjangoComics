from django.urls import path, include
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.ComicListView.as_view(), name='comic_list'),   # главная страница → каталог
    path('comic/<slug:slug>/', views.ComicDetailView.as_view(), name='comic_detail'),
    path('create/', views.ComicCreateView.as_view(), name='comic_create'),
    path('update/<slug:slug>/', views.ComicUpdateView.as_view(), name='comic_update'),
    path('delete/<slug:slug>/', views.ComicDeleteView.as_view(), name='comic_delete'),
    path('filter/', views.comic_filter_ajax, name='comic_filter'),
    path('favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('quick-view/<int:pk>/', views.quick_view, name='quick_view'),
    # Корзина
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('favorites-count/', views.favorites_count, name='favorites_count'),
    path('cart/count/', views.cart_count, name='cart_count'),
] 
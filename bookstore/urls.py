
from django.urls import path
from . import views


urlpatterns = [
    path('books_list', views.books_list),
    path('category_list', views.category_list),
    path('charge_request/', views.charge_request),
    path('charge/', views.charge),
    path('buy_book/', views.buy_book),
    path('reverse_order/', views.reverse_order),
    path('user_books', views.user_books),
    path('user_orders', views.user_orders),


]

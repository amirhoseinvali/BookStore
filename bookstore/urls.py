
from django.urls import path
from . import views


urlpatterns = [
    path('books_list', views.BooksList.as_view()),
    path('category_list', views.Category.as_view()),
    path('charge_request/', views.ChargeRequest.as_view()),
    path('charge/', views.Charge.as_view()),
    path('buy_book/', views.Buy.as_view()),
    # path('reverse_order/', views.reverse_order),
    # path('user_books', views.user_books),
    # path('user_orders', views.user_orders),


]

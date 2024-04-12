
from django.urls import path
from . import views


urlpatterns = [
    path('books_list/', views.books_list),
    path('category_list/', views.category_list),
    path('charge_request/', views.charge_request),


]

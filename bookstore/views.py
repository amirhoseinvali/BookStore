from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt import authentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Permission
from rest_framework.decorators import  permission_classes
from django.http import JsonResponse
from .models import Books, Category, UserInventory, ChargeTokens, BookOrders
from .serializers import BooksSerializer, CategorySerializer, ChargeTokensSerializer, BookOrdersSerializer
# Create your views here.



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def books_list(request):
    
    books = Books.objects.all()
    serializer = BooksSerializer(books, many = True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_list(request):
    
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many = True)
    return JsonResponse(serializer.data, safe=False)

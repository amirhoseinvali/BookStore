from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import  permission_classes
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from .models import Books, Category, UserInventory, ChargeTokens, BookOrders
from .serializers import BooksSerializer, CategorySerializer, ChargeTokensSerializer, BookOrdersSerializer



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def books_list(request):
    books = Books.objects.all()
    serializer = BooksSerializer(books, many = True)
    return JsonResponse(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many = True)
    return JsonResponse(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def charge_request(request):
    user = request.user
    otp_token = get_random_string(length=15)
    request.data['user'] = user.id
    request.data['otp_token'] = otp_token
    serializer = ChargeTokensSerializer(data = request.data)
    serializer.is_valid()
    serializer.save()
    return JsonResponse(serializer.data)
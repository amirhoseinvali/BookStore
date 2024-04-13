from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import  permission_classes
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from .models import Books, Category, UserInventory, ChargeTokens, BookOrders
from .serializers import BooksSerializer, CategorySerializer, ChargeTokensSerializer, BookOrdersSerializer,UserInventorySerializer

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def add_access_forbiden_permission():
    forbidden_group, created = Group.objects.get_or_create(name='forbidden')
    content_type = ContentType.objects.get_for_model(Permission, for_concrete_model=False)
    permission = Permission.objects.create(codename='access_forbidden_books',
                                    name='Access to forbidden books',
                                    content_type=content_type)
    forbidden_group.permissions.add(permission)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def books_list(request):
    books = Books.objects.all()
    serializer = BooksSerializer(books, many = True)
    response = MakeJsonResponse(0, MessageCodes.Successful_Operation, serializer.data)
    return JsonResponse(response, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many = True)
    response = MakeJsonResponse(0, MessageCodes.Successful_Operation, serializer.data)
    return JsonResponse(response, safe=False)


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
    response = MakeJsonResponse(0, MessageCodes.Successful_Operation, serializer.data)
    return JsonResponse(response)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def charge(request):
    otp_token = request.data['otp_token']
    try:
        token_instance = ChargeTokens.objects.get(otp_token = otp_token)
        if token_instance:
            user = token_instance.user
            amount = token_instance.amount
            if not token_instance.is_used:
                user_inventory = UserInventory.objects.get(user = user.id)
                user_current_inventory = user_inventory.inventory
                new_user_inventory = user_current_inventory + amount
                user_inventory.inventory = new_user_inventory
                user_inventory.save()
                token_instance.is_used = True
                token_instance.apply_time = datetime.now()
                token_instance.save()
                user_inventory = UserInventory.objects.get(user = user.id)
            else:
                response = MakeJsonResponse(1, MessageCodes.Token_Is_Used, {})
                return JsonResponse(response)
        else:
            response = MakeJsonResponse(1, MessageCodes.Token_Not_Found, {})
            return JsonResponse(response)
        serializer = UserInventorySerializer(user_inventory)
        response = MakeJsonResponse(0, MessageCodes.Successful_Operation, serializer.data)
        return JsonResponse(response)
    except:
            response = MakeJsonResponse(1, MessageCodes.Token_Not_Found, {})
            return JsonResponse(response)




def belong_check(user_id, book_id):
    book_order = BookOrders.objects.get(user = user_id, book = book_id, is_canceled = False)
    if book_order:
        return True
    else:
        return False


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_book(request):
    user = request.user
    user_inventory = UserInventory.objects.get(user = user.id)
    book_id = request.data['book_id']
    book_instance = Books.objects.get(id = book_id)
    forbiden_access = False
    belong = belong_check(user.id, book_id)
    if not book_instance.is_forbidden or forbiden_access:
        if not belong:
            if book_instance.quantity >= 1:
                if user_inventory.inventory >= book_instance.price:
                    order = dict()
                    order['user'] = user.id
                    order['book'] = book_id
                    order['price'] = book_instance.price
                    serializer = BookOrdersSerializer(data = order)
                    serializer.is_valid()
                    user_inventory.inventory -= book_instance.price
                    book_instance.quantity -= 1
                    book_instance.save()
                    user_inventory.save()
                    serializer.save()
                else:
                    response = MakeJsonResponse(1, MessageCodes.Inventory_Not_Enough, {})
                    return JsonResponse(response)
            else:
                response = MakeJsonResponse(1, MessageCodes.Insufficient_Quantity, {})
                return JsonResponse(response)
        else:
            response = MakeJsonResponse(1, MessageCodes.Book_Bought_Before, {})
            return JsonResponse(response)
    else:
        response = MakeJsonResponse(1, MessageCodes.Have_Not_Access, {})
        return JsonResponse(response)
    
    response = MakeJsonResponse(0, MessageCodes.Successful_Operation, order)
    return JsonResponse(response, safe=False)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reverse_order(request):

    user = request.user
    book_id = request.data['book_id']
    try:
        book_order = BookOrders.objects.get(user = user.id, book = book_id, is_canceled = False)
        if book_order:
            if book_order.order_time + timedelta(days=0, hours=-1) < datetime.now():
                book_instance = Books.objects.get(id = book_id)
                user_inventory = UserInventory.objects.get(user = user.id)
                book_order.is_canceled = True
                book_order.canceled_time = datetime.now()
                book_instance.quantity += 1
                user_inventory.inventory += book_order.price
                book_order.save()
                book_instance.save()
                user_inventory.save()
            else:
                response = MakeJsonResponse(1, MessageCodes.Allowed_Time_Has_Expired, {})
                return JsonResponse(response)
        else:
            response = MakeJsonResponse(1, MessageCodes.Never_Bought_Before, {})
            return JsonResponse(response)
        response = MakeJsonResponse(0, MessageCodes.Successful_Operation, {})
        return JsonResponse(response, safe=False)
    except:
            response = MakeJsonResponse(1, MessageCodes.Never_Bought_Before, {})
            return JsonResponse(response)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_books(request):
    user = request.user
    try:
        book_orders = BookOrders.objects.filter(user = user.id, is_canceled = False)
        if book_orders:
            serializer = BookOrdersSerializer(data = book_orders, many = True)
            serializer.is_valid()
        else:
            response = MakeJsonResponse(1, MessageCodes.Has_No_Books, {})
            return JsonResponse(response)
        response = MakeJsonResponse(0, MessageCodes.Successful_Operation, serializer.data)
        return JsonResponse(response, safe=False)
    except:
        response = MakeJsonResponse(1, MessageCodes.Has_No_Books, {})
        return JsonResponse(response)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    user = request.user
    try:
        book_orders = BookOrders.objects.filter(user = user.id)
        if book_orders:
            serializer = BookOrdersSerializer(data = book_orders, many = True)
            serializer.is_valid()
        else:
            response = MakeJsonResponse(1, MessageCodes.Has_No_Orders, {})
            return JsonResponse(response)
        response = MakeJsonResponse(0, MessageCodes.Successful_Operation, serializer.data)
        return JsonResponse(response, safe=False)
    except:
        response = MakeJsonResponse(1, MessageCodes.Has_No_Orders, {})
        return JsonResponse(response)








class MessageCodes:
    Successful_Operation = 0
    Token_Not_Found = 1
    Token_Is_Used = 2
    Inventory_Not_Enough = 3
    Insufficient_Quantity = 4
    Book_Bought_Before = 5
    Have_Not_Access = 6
    Allowed_Time_Has_Expired = 7
    Never_Bought_Before = 8
    Has_No_Books = 9
    Has_No_Orders = 10


    messages_names = {
            0: 'Successful Operation',
            1: 'The Entered Token Not Found',
            2: 'Token Is Used Before',
            3: 'Your Account Inventory Is Not Enough',
            4: 'Quantity Of This Book Is Insufficient',
            5: 'You Bought This Book Before',
            6: 'You Have Not Access To This Book',
            7: 'Allowed Time For Reverse HAs Expired',
            8: 'You Never Bought This Book Before',
            9: 'You Have Not Bought Any Books Yet',
            10: 'You Have Not Any Orders Yet'
            }



def MakeJsonResponse(status, messagecode, data=None):
    return { "Header": {
            "Status": status,
            "Message": MessageCodes.messages_names[messagecode],
            "MessageCode": messagecode 
            },
        "ContentData": data
        }

# Statuses:
# 0: success
# 1: conditional
# 2: failed
# message codes 

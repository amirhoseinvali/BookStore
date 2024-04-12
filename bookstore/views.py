from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import  permission_classes
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from .models import Books, Category, UserInventory, ChargeTokens, BookOrders
from .serializers import BooksSerializer, CategorySerializer, ChargeTokensSerializer, BookOrdersSerializer,UserInventorySerializer

# from django.contrib.auth.models import Group, Permission
# from django.contrib.contenttypes.models import ContentType

# def add_access_forbiden_permission():
#     forbidden_group, created = Group.objects.get_or_create(name='forbidden')
#     content_type = ContentType.objects.get_for_model(Permission, for_concrete_model=False)
#     permission = Permission.objects.create(codename='access_forbidden_books',
#                                     name='Access to forbidden books',
#                                     content_type=content_type)
#     forbidden_group.permissions.add(permission)


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

    serializer = UserInventorySerializer(user_inventory)
    response = MakeJsonResponse(0, MessageCodes.Successful_Operation, serializer.data)
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
    response = MakeJsonResponse(0, MessageCodes.Successful_Operation, order)
    return JsonResponse(response, safe=False)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reverse_order(request):

    user = request.user
    book_id = request.data['book_id']
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
    response = MakeJsonResponse(0, MessageCodes.Successful_Operation, {})
    return JsonResponse(response, safe=False)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_books(request):
    user = request.user
    book_orders = BookOrders.objects.filter(user = user.id, is_canceled = False)
    if book_orders:
        serializer = BookOrdersSerializer(data = book_orders, many = True)
        serializer.is_valid()
    response = MakeJsonResponse(0, MessageCodes.Successful_Operation, serializer.data)
    return JsonResponse(response, safe=False)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    user = request.user
    book_orders = BookOrders.objects.filter(user = user.id)
    if book_orders:
        serializer = BookOrdersSerializer(data = book_orders, many = True)
        serializer.is_valid()
    response = MakeJsonResponse(0, MessageCodes.Successful_Operation, serializer.data)
    return JsonResponse(response, safe=False)







class MessageCodes:
    Successful_Operation = 0
    Enter_Terminal_Id = 1
    Enter_Ticket_Number = 2
    Enter_Nationality_ID = 3
    Voucher_Info_Not_Found = 4
    Internal_Error = 5

    messages_names = {
            0: 'Successful Operation',
            1: 'Enter Terminal Number',
            2: 'Enter Ticket Number',
            3: 'Enter Nationality ID',
            4: 'Voucher Info Not Found',
            5: 'Internal Error',
            6: 'Enter Retrieval Reference Number (RRN)'
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

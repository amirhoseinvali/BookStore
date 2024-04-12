from rest_framework import serializers
from .models import Books, Category, UserInventory, ChargeTokens, BookOrders


class UserInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInventory
        fields = '__all__'



class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ChargeTokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeTokens
        fields = '__all__'


class BookOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookOrders
        fields = '__all__'
